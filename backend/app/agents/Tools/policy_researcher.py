from agents.base_agent import BaseAgent
from bs4 import BeautifulSoup
import requests
import re
from langchain_core.tools import Tool

class PolicyResearcherAgent(BaseAgent):
    """
    Researches zoning policies for a given zoning bylaw chapter.
    """
    def __init__(self):
        self.base_url = "https://www.toronto.ca/zoning/bylaw_amendments"
        tools = [
            Tool(
                name="Scrape Toronto Zoning Bylaws",
                func = self.scrape_toronto_zoning_bylaws,
                description="Use this tool to scrape the Toronto Zoning Bylaws for a specific zoning bylaw chapter"
            )
        ]

        super().__init__(tools=tools)


    def scrape_toronto_zoning_bylaws(self, chapter_number: str) -> str:
        try:
            chapter_parts = chapter_number.split('.')
            formatted_chapter = '_'.join(chapter_parts)

            url = f"{self.base_url}/ZBL_NewProvision_Chapter{formatted_chapter}.htm"
            response = requests.get(url)

            soup = BeautifulSoup(response.text, 'html.parser')

            content = ""
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    text = cells[1].get_text().strip()
                    content += text + "\n"

            if not content:
                content = soup.get_text()
            
            text = re.sub(r'\s+', ' ', content.strip())
            return text[:6000]  # Limit length for LLM processing
            
        except Exception as e:
            return f"Error scraping Toronto Zoning Bylaws: {e}"
    
    async def process(self, context: dict) -> dict:
        zone_section = context.get("bylaw_section")
        zone_type = context.get("zone_type")
        if not zone_section:
            return {"error": "No zoning bylaw chapter provided"}
            
        bylaw_text = await self.ainvoke_tool("Scrape Toronto Zoning Bylaws", zone_section)

        prompt = f"""
        You are a zoning policy researcher for the City of Toronto.
        You are given a zoning bylaw chapter and a zoning bylaw section.
        
        Based on the following zoning bylaw text for zone type {zone_type}, 
        extract the key policies and restrictions:
        
        {bylaw_text}
        
        Summarize the most important regulations in a clear, concise format.
        """

        response = await self.llm.ainvoke(prompt)

        split_section = zone_section.split('.')
        formatted_section = '_'.join(split_section)
        url = f"{self.base_url}/ZBL_NewProvision_Section{formatted_section}.htm"

        return {
            "zone_type": zone_type,
            "bylaw_section": formatted_section,
            "policies": response,
            "source": url
        }