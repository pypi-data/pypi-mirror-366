import os
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from groq import Groq
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Optional, ClassVar, Any, List, Mapping
from langchain_core.language_models import BaseLLM
import pandas as pd
from IPython.display import Markdown, display




# === 1. Groq Multimodal Plot Explainer ===
class AgentExecutor:
    def __init__(self, model="meta-llama/llama-4-maverick-17b-128e-instruct"):
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))
        self.model = model

    def plot_to_base64(self, fig=None):
        buf = BytesIO()
        if fig is None:
            fig = plt.gcf()
        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{encoded}"

    def explain_plot_from_data_url(self, image_data_url: str, user_text: str = "") -> str:
        try:
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_text + "\n\nAnalyze this plot and provide 2–4 key insights with a conclusion."},
                        {"type": "image_url", "image_url": {"url": image_data_url}}
                    ]
                }
            ]
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=1,
                top_p=1,
                max_tokens=1024,
                stream=False,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error analyzing plot with Groq API: {str(e)}"


# === 2. LangChain Tool Wrapper ===
class PlotInsightInput(BaseModel):
    image_data_url: str = Field(..., description="Base64 encoded image data URL")
    user_text: str = Field("", description="Optional context or question")

class PlotInsightTool(BaseTool):
    name: ClassVar[str] = "plot_insight_tool"
    description: ClassVar[str] = "Analyze a data plot and provide insights"
    args_schema: ClassVar[Type[BaseModel]] = PlotInsightInput
    explainer: AgentExecutor = Field(default_factory=AgentExecutor)

    def _run(self, image_data_url: str, user_text: str = "") -> str:
        try:
            return self.explainer.explain_plot_from_data_url(image_data_url, user_text)
        except Exception as e:
            return f"Error in plot analysis tool: {str(e)}"




def analyze_plot_with_insight_agent(fig, user_text: str = ""):
    explainer = AgentExecutor()
    image_data_url = explainer.plot_to_base64(fig)
    tool = PlotInsightTool()
    analysis = tool.run({
        "image_data_url": image_data_url,
        "user_text": user_text
    })
    return display(Markdown(analysis))