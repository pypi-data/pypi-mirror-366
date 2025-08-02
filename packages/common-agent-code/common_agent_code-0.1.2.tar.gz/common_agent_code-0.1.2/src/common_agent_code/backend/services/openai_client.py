from openai import AzureOpenAI
import os

client = AzureOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY", "your-api-key-here"),
    api_version="2024-02-15-preview",
    azure_endpoint="https://radiusofself.openai.azure.com",
    azure_deployment="gpt-4o"
)