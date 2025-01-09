import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Tuple, Optional
from serpapi import GoogleSearch
import numpy as np
from deap import base, creator, tools, algorithms
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def clean_product_name(name: str) -> str:
    # Remove common suffixes and prefixes
    suffixes = ['es', 's']
    for suffix in suffixes:
        if name.lower().endswith(suffix):
            name = name[:-len(suffix)]
            break
    
    # Remove any non-alphanumeric characters and convert to lowercase
    return ''.join(char.lower() for char in name if char.isalnum())

def get_market_prices(produce_name: str) -> List[Dict[str, str]]:
    urls = [
        "https://vegetablemarketprice.com/market/bangalore/today",
        "https://vegetablemarketprice.com/fruits/karnataka/today",
        "https://vegetablemarketprice.com/nonveg/bangalore/today"
    ]

    market_prices = []
    cleaned_produce_name = clean_product_name(produce_name)

    for url in urls:
        try:
            logger.debug(f"Fetching market prices from {url}")
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            rows = soup.find_all('tr')

            for row in rows[1:]:
                cells = row.find_all('td')
                if len(cells) >= 5:
                    item_name = cells[1].text.strip().lower()
                    cleaned_item_name = clean_product_name(item_name)
                    if cleaned_produce_name in cleaned_item_name or any(word in cleaned_item_name for word in cleaned_produce_name.split()):
                        wholesale_price = extract_price_value(cells[2].text)
                        retail_price = extract_price_range(cells[3].text)
                        shopping_mall_price = extract_price_range(cells[4].text)
                        unit = cells[5].text.strip() if len(cells) > 5 else "1kg"

                        logger.debug(f"Found price data for {produce_name}: Wholesale={wholesale_price}, Retail={retail_price}, Shopping Mall={shopping_mall_price}")

                        market_prices.append({
                            "source": "Vegetable Market Price",
                            "type": "Wholesale",
                            "price": f"₹{wholesale_price:.2f}" if wholesale_price else "N/A",
                            "unit": unit
                        })

                        if retail_price:
                            market_prices.append({
                                "source": "Vegetable Market Price",
                                "type": "Retail",
                                "price": f"₹{retail_price[0]:.2f} - ₹{retail_price[1]:.2f}",
                                "unit": unit
                            })

                        if shopping_mall_price:
                            market_prices.append({
                                "source": "Vegetable Market Price",
                                "type": "Shopping Mall",
                                "price": f"₹{shopping_mall_price[0]:.2f} - ₹{shopping_mall_price[1]:.2f}",
                                "unit": unit
                            })

                        return market_prices

        except Exception as e:
            logger.error(f"Error fetching market prices from {url}: {e}")

    logger.warning(f"No market prices found for {produce_name}")
    return market_prices

def extract_price_value(text: str) -> Optional[float]:
    match = re.search(r'₹?(\d+(?:\.\d{2})?)', text.strip())
    return float(match.group(1)) if match else None

def extract_price_range(text: str) -> Optional[Tuple[float, float]]:
    matches = re.findall(r'₹?(\d+(?:\.\d{2})?)', text.strip())
    if len(matches) >= 2:
        return float(matches[0]), float(matches[1])
    return None

def get_online_retail_prices(produce_name: str) -> List[Dict[str, str]]:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        logger.error("SERPAPI_API_KEY not found in environment variables")
        return []

    retailers = ["bigbasket", "jiomart", "instamart", "blinkit", "oneindia"]
    prices = []
    cleaned_produce_name = clean_product_name(produce_name)

    for retailer in retailers:
        params = {
            "engine": "google",
            "q": f"{produce_name} price {retailer} bangalore",
            "api_key": api_key,
            "num": 5,
            "location": "Bangalore, Karnataka, India",
            "gl": "in",
            "hl": "en"
        }

        try:
            logger.debug(f"Sending request to SerpAPI for {retailer}: {params}")
            search = GoogleSearch(params)
            results = search.get_dict()

            if "error" in results:
                logger.error(f"SerpAPI error for {retailer}: {results['error']}")
                if "Invalid API key" in results['error']:
                    logger.error("Please check your SERPAPI_API_KEY in the environment variables")
                continue

            logger.debug(f"Received response from SerpAPI for {retailer}: {results}")

            if "organic_results" in results:
                for result in results["organic_results"]:
                    title = result.get("title", "")
                    snippet = result.get("snippet", "")
                    link = result.get("link", "")

                    if retailer.lower() in link.lower():
                        price_info = extract_price_and_weight(title, snippet)
                        if price_info:
                            original_price, discounted_price, weight = price_info
                            if original_price and weight:
                                price_per_kg = calculate_price_per_kg(
                                    discounted_price or original_price,
                                    weight
                                )

                                prices.append({
                                    "source": retailer.capitalize(),
                                    "type": "Online Retail",
                                    "price_per_kg": f"₹{price_per_kg:.2f}",
                                    "original_price": f"₹{original_price:.2f}",
                                    "discounted_price": f"₹{discounted_price:.2f}" if discounted_price else None,
                                    "unit": f"{weight[0]} {weight[1]}",
                                    "website": link
                                })
                                break

        except Exception as e:
            logger.error(f"Error searching for {retailer}: {e}")

    return prices

def extract_price_and_weight(title: str, snippet: str) -> Optional[Tuple[float, float, tuple]]:
    text = f"{title} {snippet}"

    price_pattern = r'(?:₹|Rs\.?)\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
    prices = re.findall(price_pattern, text)

    if not prices:
        return None

    prices = [float(p.replace(',', '')) for p in prices]

    prices.sort(reverse=True)
    original_price = prices[0]
    discounted_price = prices[1] if len(prices) > 1 and prices[1] < prices[0] else None

    weight_match = re.search(r'(\d+(?:\.\d+)?)\s*(kg|g)\b', text, re.IGNORECASE)
    if not weight_match:
        return None

    weight_value = float(weight_match.group(1))
    weight_unit = weight_match.group(2).lower()

    return original_price, discounted_price, (weight_value, weight_unit)

def calculate_price_per_kg(price: float, weight: tuple) -> float:
    weight_value, weight_unit = weight
    if weight_unit == 'kg':
        return price / weight_value
    elif weight_unit == 'g':
        return price / (weight_value / 1000)
    return None

def optimize_price(produce_name, production_cost, min_price, max_price, market_prices, online_prices):
    logger.info(f"Optimizing price for {produce_name}")
    logger.debug(f"Input parameters: production_cost={production_cost}, min_price={min_price}, max_price={max_price}")
    
    if not market_prices and not online_prices:
        logger.warning(f"No market or online prices found for {produce_name}")
        return None

    logger.debug(f"Market prices: {market_prices}")
    logger.debug(f"Online prices: {online_prices}")

    # Process market data
    market_data = []
    for price in market_prices + online_prices:
        if 'price' in price:
            if isinstance(price['price'], str) and '-' in price['price']:
                low, high = map(float, price['price'].replace('₹', '').split('-'))
                market_data.append((low + high) / 2)
            elif isinstance(price['price'], str):
                market_data.append(float(price['price'].replace('₹', '')))
        elif 'price_per_kg' in price:
            market_data.append(float(price['price_per_kg'].replace('₹', '')))

    logger.debug(f"Processed market data for {produce_name}: {market_data}")

    if not market_data:
        logger.warning(f"No market data available for {produce_name}")
        return None

    # Define fitness function
    def evaluate(individual):
        price = individual[0]
        profit = (price - production_cost) * (100 - price)  # Simple demand curve
        market_alignment = -sum((price - mp)**2 for mp in market_data)  # Penalty for deviating from market prices
        return profit + market_alignment,

    # Set up genetic algorithm
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_float", np.random.uniform, min_price, max_price)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_float, n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate)
    toolbox.register("mate", tools.cxBlend, alpha=0.5)
    toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=1, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Run genetic algorithm
    population = toolbox.population(n=50)
    algorithms.eaSimple(population, toolbox, cxpb=0.5, mutpb=0.2, ngen=50, verbose=False)

    # Get best individual
    best_ind = tools.selBest(population, k=1)[0]
    optimized_price = best_ind[0]

    logger.info(f"Optimized price for {produce_name}: ₹{optimized_price:.2f}")
    logger.debug(f"Market data used for optimization: {market_data}")
    return optimized_price

