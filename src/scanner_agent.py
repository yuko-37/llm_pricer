from openai import OpenAI
from deals import ScrapedDeal, DealSelection


class ScannerAgent:

    MODEL = "gpt-5-nano"

    INSTRUCTIONS = """You identify and summarize the 5 most detailed deals from a list, by selecting deals that have 
the most detailed, high quality description and the most clear price.
Respond strictly in JSON with no explanation, using this format. You should provide the price as a number derived 
from the description. If the price of a deal isn't clear, do not include that deal in your response.
Most important is that you respond with the 5 deals that have the most detailed product description with price. 
It's not important to mention the terms of the deal; most important is a thorough description of the product.
Be careful with products that are described as "$XXX off" or "reduced by $XXX" - this isn't the actual price of the 
product. Only respond with products when you are highly confident about the price. 

{"deals": [
    {
        "product_description": "Your clearly expressed summary of the product in 4-5 sentences. Details of the item 
        are much more important than why it's a good deal. Avoid mentioning discounts and coupons; focus on the 
        item itself. There should be a paragraph of text for each item you choose.",
        "price": 99.99,
        "url": "the url as provided"
    },
    ...
]}"""

    USER_PROMPT_PREFIX = """Respond with the most promising 5 deals from this list, selecting those which have the most 
detailed, high quality product description and a clear price that is greater than 0.
Respond strictly in JSON, and only JSON. You should rephrase the description to be a summary of the product itself, 
not the terms of the deal.
Remember to respond with a paragraph of text in the product_description field for each of the 5 items that you 
select.
Be careful with products that are described as "$XXX off" or "reduced by $XXX" - this isn't the actual price of the 
product. Only respond with products when you are highly confident about the price. 

Deals:

"""
    USER_PROMPT_SUFFIX = (
        "\n\nStrictly respond in JSON and include exactly 5 deals, no more."
    )

    def __init__(self):
        self.client = OpenAI()

    def scan(self):
        result = []
        try:
            scraped_deals = ScrapedDeal.fetch()
            if scraped_deals:
                scraped_deals_str = "\n\n".join([sd.describe() for sd in scraped_deals])
                user_input = f"{self.USER_PROMPT_PREFIX}{scraped_deals_str}{self.USER_PROMPT_SUFFIX}"

                response = self.client.responses.parse(
                    model=self.MODEL,
                    instructions=self.INSTRUCTIONS,
                    input=user_input,
                    text_format=DealSelection,
                )

                result = response.output_parsed
                result.deals = [deal for deal in result.deals if deal.price > 0]
        except Exception as ex:
            print(f"Failed to scan for deals: {ex}")

        return result
