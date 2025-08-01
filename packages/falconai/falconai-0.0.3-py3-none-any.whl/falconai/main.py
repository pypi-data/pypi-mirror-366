import os
os.environ["ANONYMIZED_TELEMETRY"] = "false"


class ai:
    def __init__(self):
        self.model = "o4-mini"
        self.mlops = False
        self.exp_name = "Tracing Demo"
        self.media_ready = 0
        self.final_prompt = None
        self.output_type = "text"
        self.media = ""
        self.web = False
        self.model_provider = ""
        self.free = False

    def encode_image(self, image_path):
        import base64

        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def search_tool_async_scrape(self, ddg_results):
        results = []
        try:
            from crawl4ai import AsyncWebCrawler
            async with AsyncWebCrawler() as crawler:
                for item in ddg_results:
                    url = item.get('href') or "N/A"
                    content = item.get('body', "")

                    if url != "N/A":
                        try:
                            full_content = await crawler.arun(url=url)

                        except Exception:
                            full_content = "Error: Unable to crawl this URL"
                            full_content = full_content.markdown
                    else:
                        full_content = "No URL provided for crawling"

                    results.append({
                        "content": content,
                        "url": url,
                        "full_content": full_content
                    })

        except Exception as e:
            print(f"Web scrapping error: {e}")
        return results

    def search_tool(self, query):
        import asyncio
        try:
            from duckduckgo_search import DDGS
            ddg_results = list(DDGS().text(query, max_results=2))
            return asyncio.run(self.search_tool_async_scrape(ddg_results))
        except Exception as e:
            print(f"search_tool error: {e}")

    @staticmethod
    def chat(prompt, **kwargs):
        import litellm
        instance = ai()
        instance.model_provider = ""
        browser = kwargs.get("browser", False)
        instance.output_type = kwargs.get("output_type", "text")
        voice_name = kwargs.get("voice_name", "falconai.mp3")
        if voice_name != "falconai.mp3":
            voice_name = voice_name+".mp3"
        voice_speed = kwargs.get("voice_speed", 140)
        voice_volume = kwargs.get("voice_volume", 1.0)
        voice_type = kwargs.get("voice_type", int(1))  # default female = 1
        free = kwargs.get("free", False)
        browser_headless = kwargs.get("browser_headless", False)
        # browser_path = kwargs.get("browser_path", False)
        mcp = kwargs.get("MCP", False)
        mcp_builtin_server = kwargs.get("MCP_builtin_server", False)
        mcp_custom_server = kwargs.get("MCP_custom_server", False)
        mcp_agent_max_steps = kwargs.get("MCP_agent_max_steps", int(30))
        mcp_agent_max_steps = int(mcp_agent_max_steps)
        mcp_agent_system_prompt = kwargs.get("MCP_agent_system_prompt", False)
        mcp_agent_chat = kwargs.get("MCP_agent_chat", False)
        mcp_user_reply = kwargs.get("MCP_user_reply", False)
        browser_system_prompt = kwargs.get("browser_system_prompt", False)

        if voice_type == "male":
            voice_type = int(0)
        web = kwargs.get("web", instance.web)
        model = kwargs.get("model", instance.model)

        # Comming soon!
        # mlops = kwargs.get("mlops", instance.mlops)
        # exp_name = kwargs.get("exp_name", instance.exp_name)

        test_output = kwargs.get("test_output", None)

        image = kwargs.get("image", "")

        csv = kwargs.get("csv", "")

        ipynb = kwargs.get("ipynb", "")

        website = kwargs.get("website", "")

        pdf = kwargs.get("pdf", "")

        youtube = kwargs.get("youtube", "")

        text = kwargs.get("text", "")

        markdown = kwargs.get("markdown", "")

        document = kwargs.get("document", "")

        html = kwargs.get("html", "")

        if image.startswith("http"):
            instance.media_ready = 1

        if image and instance.media_ready == 0:
            base64_image = instance.encode_image(image)
            instance.media_ready = 2

        valid_keywords = ['output_type', 'voice_name', 'voice_speed', 'voice_volume', 'voice_type', 'web', 'model', 'test_output', 'image', 'csv', 'ipynb', 'website', 'pdf', 'text', 'markdown', 'document', 'youtube',
                          'html', 'browser', 'browser_headless', 'browser_path', 'browser_system_prompt', 'free', 'MCP', 'MCP_builtin_server', 'MCP_custom_server', 'MCP_agent_max_steps', 'MCP_agent_system_prompt', 'MCP_agent_chat', 'MCP_user_reply']

        for key in kwargs:

            if key not in valid_keywords:
                raise ValueError(f"Invalid keyword: {key}")

            if instance.output_type == "text" and (key == "voice_speed" or key == "voice_volume" or key == "voice_type" or key == "voice_name"):
                raise ValueError(
                    f"To use the keyword {key} first set the keyword output_type='voice'")

            if browser == False and (key == "browser_headless" or key == "browser_path" or key == " browser_system_prompt"):
                raise ValueError(
                    f"To use the keyword {key} first set the keyword browser=True")

            if browser and key not in ['model', 'browser', 'mlops', 'browser_headless', 'browser_path', 'browser_system_prompt']:
                raise ValueError(f"Cannot use keyword:{key} when browser=True")

            if mcp == False and (key == "MCP_builtin_server" or key == "MCP_custom_server" or key == "MCP_agent_max_steps" or key == "MCP_agent_system_prompt" or key == "MCP_agent_chat" or key == "MCP_user_reply"):
                raise ValueError(
                    f"To use the keyword {key} first set the keyword MCP=True")

            if mcp and key not in ["model", "MCP", "MCP_builtin_server", "MCP_custom_server", "MCP_agent_max_steps", "MCP_agent_system_prompt", "MCP_agent_chat", "MCP_user_reply"]:
                raise ValueError(f"Cannot use keyword:{key} when MCP=True")

        if mcp and not any(k in kwargs for k in ["MCP_builtin_server", "MCP_custom_server"]):
            raise ValueError(
                "When MCP=True, you must provide either 'MCP_builtin_server' or 'MCP_custom_server' or both")

        if csv:
            import os
            import tempfile
            from langchain_community.document_loaders.csv_loader import CSVLoader
            if isinstance(csv, str) and os.path.isfile(csv):
                loader = CSVLoader(file_path=csv, encoding='utf-8')
                instance.media = loader.load()
            else:
                if hasattr(csv, "getvalue"):
                    raw = csv.getvalue()
                elif hasattr(csv, "read"):
                    raw = csv.read()
                else:
                    raise ValueError(
                        "`csv` must be a file path or a file-like object with getvalue()/read()")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = CSVLoader(file_path=tmp_path, encoding='utf-8')
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if ipynb:
            import os
            import tempfile
            from langchain_community.document_loaders import NotebookLoader
            if isinstance(ipynb, str) and os.path.isfile(ipynb):
                loader = NotebookLoader(ipynb, include_outputs=True)
                instance.media = loader.load()
            else:
                if hasattr(ipynb, "getvalue"):
                    raw = ipynb.getvalue()
                elif hasattr(ipynb, "read"):
                    raw = ipynb.read()
                else:
                    raise ValueError(
                        "`ipynb` must be a file path or a file-like object with getvalue()/read()")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".ipynb", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = NotebookLoader(tmp_path, include_outputs=True)
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if website:
            from langchain_community.document_loaders import WebBaseLoader

            loader = WebBaseLoader(website)

            full_html = loader.load()
            raw_html = "".join(doc.page_content for doc in full_html)
            clean_html = raw_html.replace("\n", "")
            instance.media = clean_html

        if pdf:
            import os
            import tempfile
            from langchain_community.document_loaders import PyPDFLoader

            if isinstance(pdf, str) and os.path.isfile(pdf):
                loader = PyPDFLoader(pdf)
                instance.media = loader.load()

            else:

                if hasattr(pdf, "getvalue"):
                    raw = pdf.getvalue()
                elif hasattr(pdf, "read"):
                    raw = pdf.read()
                else:
                    raise ValueError(
                        "`pdf` must be either a file-path string or a file-like with getvalue()/read()")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = PyPDFLoader(tmp_path)
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if youtube:
            from langchain_community.document_loaders import YoutubeLoader
            loader = YoutubeLoader.from_youtube_url(
                youtube,
                add_video_info=False
            )

            instance.media = loader.load()

        if text or markdown:
            import os
            import tempfile
            from langchain_community.document_loaders import TextLoader
            input_obj = markdown if markdown else text
            if isinstance(input_obj, str) and os.path.isfile(input_obj):
                loader = TextLoader(input_obj, encoding="utf-8")
                instance.media = loader.load()
            else:
                if hasattr(input_obj, "getvalue"):
                    raw = input_obj.getvalue()
                elif hasattr(input_obj, "read"):
                    raw = input_obj.read()
                else:
                    raise ValueError(
                        "`text`/`markdown` must be a file path or a file-like object")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = TextLoader(tmp_path, encoding="utf-8")
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if document:
            import os
            import tempfile
            from langchain_community.document_loaders import Docx2txtLoader
            if isinstance(document, str) and os.path.isfile(document):
                loader = Docx2txtLoader(document)
                instance.media = loader.load()
            else:
                if hasattr(document, "getvalue"):
                    raw = document.getvalue()
                elif hasattr(document, "read"):
                    raw = document.read()
                else:
                    raise ValueError(
                        "`document` must be a file path or a file-like object")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = Docx2txtLoader(tmp_path)
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if html:
            import os
            import tempfile
            from langchain_community.document_loaders import BSHTMLLoader
            if isinstance(html, str) and os.path.isfile(html):
                loader = BSHTMLLoader(file_path=html)
                instance.media = loader.load()
            else:
                if hasattr(html, "getvalue"):
                    raw = html.getvalue()
                elif hasattr(html, "read"):
                    raw = html.read()
                else:
                    raise ValueError(
                        "`html` must be a file path or a file-like object")

                if isinstance(raw, str):
                    raw = raw.encode("utf-8")

                with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
                    tmp.write(raw)
                    tmp_path = tmp.name

                try:
                    loader = BSHTMLLoader(file_path=tmp_path)
                    instance.media = loader.load()
                finally:
                    os.remove(tmp_path)

        if web == False:
            if instance.media == "":
                instance.final_prompt = f"""
                You are a highly capable assistant designed to provide detailed, comprehensive, and accurate responses to complex queries based solely on factual knowledge.

    Analyze the provided query thoroughly and generate a detailed response based on your understanding and expertise. Your response must:

    Address the query fully and comprehensively.
    Answer must be structured and detailed
    Present information in a clear, concise, and easy-to-understand format.
    Include all relevant insights and avoid assumptions or unrelated details.
    The query is as follows:
    "{prompt}"
    """

            if not instance.media == "":
                instance.final_prompt = f"""
        You are a highly capable assistant designed to extract and summarize information
        from multiple documents in various formats, such as DOCX, PPTX, PDF, TXT, Markdown, and others.

        The provided documents are as follows: {instance.media}

        Thoroughly analyze the content of these documents and generate a detailed response to the query below:
        "{prompt}"

        Only use factual information found within the documents to generate your response.
        Do not include assumptions or unrelated information in your output.

        Always ensure your output is factually accurate, verbose, and addresses the query fully.
        """
        if web == True:
            if instance.media == "":
                instance.final_prompt = f"""
                You have to create a prompt for a search tool based on a this query:{prompt}.
Output Format:
A clear and optimized query string ready for execution. No double quotes
Your output will be entered in a search engine to get realtime data so it must be only one sentence long.It should not exceed 20 words
    """

            if not instance.media == "":
                instance.final_prompt = f"""
The input consists of the following:
1. Documents: A list of sources or content references denoted as {instance.media}.
2. Query: A specific question or requirement stated as "{prompt}".

        """
        # Comming soon!!

        # if mlops:
        #     try:
        #         import mlflow
        #         import time
        #         mlflow.set_experiment(exp_name)
        #         mlflow.litellm.autolog()

        #     except Exception as e:
        #         print(f"Error enabling MLflow autolog: {e}")

        import os
        if model.startswith("gemini/"):
            api_key = os.getenv("GEMINI_API_KEY")
            instance.model_provider = "Google"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'GEMINI_API_KEY'")

        elif model.startswith("claude/"):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            instance.model_provider = "Anthropic"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'ANTHROPIC_API_KEY'")

        elif model.startswith("bedrock/"):
            api_key1 = os.getenv("AWS_ACCESS_KEY_ID")
            api_key2 = os.getenv("AWS_SECRET_ACCESS_KEY")
            api_key3 = os.getenv("AWS_REGION_NAME")
            if not api_key1 or not api_key2 or not api_key3:
                raise ValueError(
                    "API keys not found in environment variables. Name your APIs keys as 'AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY' and 'AWS_REGION_NAME'")

        elif model.startswith("mistral/"):
            api_key = os.getenv("MISTRAL_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'MISTRAL_API_KEY'")

        elif model.startswith("huggingface/"):
            api_key = os.getenv("HF_TOKEN")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'HUGGINGFACE_API_KEY'")

        elif model.startswith("nvidia_nim/"):
            api_key = os.getenv("NVIDIA_NIM_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'NVIDIA_NIM_API_KEY'")

        elif model.startswith("xai/"):
            api_key = os.getenv("XAI_API_KEY")
            instance.model_provider = "X AI"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'XAI_API_KEY'")

        elif model.startswith("cerebras/"):
            api_key = os.getenv("CEREBRAS_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'CEREBRAS_API_KEY'")

        elif model.startswith("perplexity/"):
            api_key = os.getenv("PERPLEXITYAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'PERPLEXITYAI_API_KEY'")

        elif model.startswith("openrouter/"):
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'OPENROUTER_API_KEY'")

        elif model.startswith("deepseek/"):
            api_key = os.getenv("DEEPSEEK_API_KEY")
            instance.model_provider = "DeepSeek"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'DEEPSEEK_API_KEY'")

        elif model.startswith("sambanova/"):
            api_key = os.getenv("SAMBANOVA_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'SAMBANOVA_API_KEY'")

        elif model.startswith("together_ai/"):
            api_key = os.getenv("TOGETHERAI_API_KEY")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'TOGETHERAI_API_KEY'")

        elif model.startswith("lm_studio/"):
            api_key = os.getenv("LM_STUDIO_API_BASE")
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'LM_STUDIO_API_BASE'")

        elif model.startswith("groq/"):
            api_key = os.getenv("GROQ_API_KEY")
            instance.model_provider = "groq"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'GROQ_API_KEY'")

        elif model.startswith("github/"):
            api_key = os.getenv("GITHUB_API_KEY")
            instance.model_provider = "Github"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'GITHUB_API_KEY'")

        elif model.startswith("meta_llama/"):
            api_key = os.getenv("LLAMA_API_KEY")
            instance.model_provider = "Meta"
            if not api_key:
                raise ValueError(
                    "API key not found in environment variables. Name your API key as 'LLAMA_API_KEY'")

        else:
            if not free:
                api_key = os.getenv("OPENAI_API_KEY")
                instance.model_provider = "OpenAI"
                if not api_key:
                    raise ValueError(
                        "API key not found in environment variables. Name your API key as 'OPENAI_API_KEY'")

        if instance.final_prompt:
            content = [

                {
                    "type": "text",
                    "text": instance.final_prompt
                }
            ]
        else:
            content = [

                {
                    "type": "text",
                    "text": prompt
                }
            ]

        if image:
            if not litellm.supports_vision(model):
                raise AssertionError(
                    "The provided model does not support images as input!")

            if instance.media_ready == 1:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": image}
                })

            if instance.media_ready == 2:
                content.append({
                    "type": "image_url",
                    "image_url": {"url": "data:image/jpeg;base64," + base64_image}
                })
        # Coming soon!
        if free and model.startswith("free/"):
            import requests

            candidates = [
                "llama",
                "openai-large",
                "gemini",
                "mistral"
            ]

            free_model = next((m for m in candidates if m in model), None)

            if free_model:
                url = "https://text.pollinations.ai/"+instance.final_prompt+"model="+free_model
                results = requests.get(url)
                # print(results.text)
                return results.text
            else:
                raise ValueError(
                    "The supported models for free inference are "
                    "llama, openai-large, gemini and mistral"
                )

        completion_args = {
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": content
                }
            ]
        }

        if test_output:
            completion_args["mock_response"] = test_output

###
        # Langchain equivalent
        from langchain_openai import ChatOpenAI
        from langchain_groq import ChatGroq
        from langchain_anthropic import ChatAnthropic
        from langchain_xai import ChatXAI
        from langchain_google_genai import ChatGoogleGenerativeAI
        from langchain_deepseek import ChatDeepSeek
        from browser_use.llm import ChatGoogle as browserChatGoogle
        from browser_use.llm import ChatOpenAI as browserChatOpenai
        from browser_use.llm import ChatAnthropic as browserChatAnthropic
        from browser_use.llm import ChatGroq as browserChatGroq
        from browser_use.llm import ChatDeepSeek as browserChatDeepSeek
        from browser_use.llm import ChatDeepSeek as browserChatDeepSeek

        if instance.model_provider == "Github":
            os.environ['OPENAI_API_KEY'] = api_key
            os.getenv('OPENAI_API_KEY')
            langchain_model = model.split("/")[-1]
            llm = ChatOpenAI(
                base_url="https://models.inference.ai.azure.com", model=langchain_model)
            browserllm = browserChatOpenai(
                base_url="https://models.inference.ai.azure.com", model=langchain_model)

        if instance.model_provider == "Anthropic":
            langchain_model = model.split("/")[-1]
            llm = ChatAnthropic(model_name=langchain_model)
            browserllm = browserChatAnthropic(model=langchain_model)

        if instance.model_provider == "OpenAI":
            llm = ChatOpenAI(model=model)
            browserllm = browserChatOpenai(model=langchain_model)

        if instance.model_provider == "Google":
            os.environ['GOOGLE_API_KEY'] = api_key
            os.getenv('GOOGLE_API_KEY')
            langchain_model = model.split("/")[-1]
            llm = ChatGoogleGenerativeAI(model=langchain_model)
            browserllm = browserChatGoogle(model=langchain_model)

        if instance.model_provider == "DeepSeek":
            os.environ['DEEPSEEK_API_KEY'] = api_key
            os.getenv('DEEPSEEK_API_KEY')
            langchain_model = model.split("/")[-1]
            llm = ChatDeepSeek(model=langchain_model)
            browserllm = browserChatDeepSeek(model=langchain_model)

        if instance.model_provider == "X AI":
            os.environ['GROK_API_KEY'] = api_key
            os.getenv('GROK_API_KEY')
            langchain_model = model.split("/")[-1]
            llm = ChatXAI(model=langchain_model)
            browserllm = browserChatOpenai(
                base_url="https://api.x.ai/v1", model=langchain_model)

        if instance.model_provider == "groq":
            os.environ['GROQ_API_KEY'] = api_key
            os.getenv('GROQ_API_KEY')
            langchain_model = model.split("/")[-1]
            llm = ChatGroq(model=langchain_model)
            browserllm = browserChatGroq(model=langchain_model)

        if browser == True:

            import asyncio
            from browser_use import Agent, Browser, BrowserConfig, Controller, ActionResult

            browser1 = Browser(
                config=BrowserConfig(
                    headless=browser_headless,
                )
            )

            controller = Controller()

            @controller.action('Ask user for information')
            def ask_human(question: str) -> str:
                answer = input(f'\n{question}\nInput: ')
                return ActionResult(extracted_content=answer)

            if instance.model_provider not in ["OpenAI", "Anthropic", "Github", "Google", "DeepSeek", "X AI", "groq"]:
                raise ValueError(
                    "For browser automation the supported models can only be from Anthropic, OpenAI, Google, X AI, DeepSeek or Groq")

            agent_kwargs = {
                "task": prompt,
                "llm": browserllm,
                "controller": controller,
                "browser": browser1,
                "validate_output": True,
            }

            if browser_system_prompt:
                agent_kwargs["extend_system_message"] = browser_system_prompt

            async def run_agent_and_extract():
                agent = Agent(
                    **agent_kwargs
                )

                result = await agent.run()

                return result.final_result()

            return (asyncio.run(run_agent_and_extract()))

# MCP
        if mcp == True:
            from mcp_use import MCPAgent, MCPClient
            import asyncio
            import json

            def load_custom_servers(config):
                if isinstance(config, str):
                    if os.path.isfile(config):
                        with open(config, 'r') as f:
                            data = json.load(f)
                            if "mcpServers" not in data:
                                raise ValueError(
                                    "JSON file must contain a top-level 'mcpServers' key")
                            return data["mcpServers"]
                    else:
                        try:
                            parsed = json.loads(config)
                            if "mcpServers" not in parsed:
                                raise ValueError(
                                    "Custom server JSON string must contain a top-level 'mcpServers' key")
                            return parsed["mcpServers"]
                        except json.JSONDecodeError:
                            raise ValueError(
                                "Provided MCP_custom_server string is neither a valid path nor valid JSON")
                elif isinstance(config, dict):
                    if "mcpServers" not in config:
                        raise ValueError(
                            "Custom MCP server dict must contain a top-level 'mcpServers' key")
                    return config["mcpServers"]
                else:
                    raise ValueError(
                        "MCP_custom_server must be a dict, a JSON string, or a path to a JSON file")

            builtin_mcp_servers_list = {
                "desktop-commander": {
                    "command": "npx",
                    "args": ["-y", "@wonderwhy-er/desktop-commander"]
                },
                "biomcp": {
                    "command": "uv",
                    "args": ["run", "--with", "biomcp-python", "biomcp", "run"]
                },
                "word-document-server": {
                    "command": "uvx",
                    "args": [
                        "--from",
                        "office-word-mcp-server",
                        "word_mcp_server"
                    ]
                },
                "puppeteer": {
                    "command": "npx",
                    "args": ["-y", "@modelcontextprotocol/server-puppeteer"]
                },
                "blender": {
                    "command": "uvx",
                    "args": [
                        "blender-mcp"
                    ]
                },
                "hackernews": {
                    "command": "uvx",
                    "args": ["mcp-hn"]
                },
                "sequential-thinking": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-sequential-thinking"
                    ]

                },
                "fetch": {
                    "command": "uvx",
                    "args": ["mcp-server-fetch"]
                },
                "ppt": {
                    "command": "uvx",
                    "args": [
                        "--from", "office-powerpoint-mcp-server", "ppt_mcp_server"
                    ],
                },
                "airbnb": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@openbnb/mcp-server-airbnb",
                        "--ignore-robots-txt"
                    ]
                },
                "app-insight-mcp": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@jeromyfu/app-insight-mcp"
                    ]
                },
                "excel": {
                    "command": "uvx",
                    "args": ["excel-mcp-server", "stdio"]
                },
                "textEditor": {
                    "command": "npx",
                    "args": ["-y", "mcp-server-text-editor"]
                },
                "memory": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@modelcontextprotocol/server-memory"
                    ]
                },
                "mcp-docker": {
                    "command": "uvx",
                    "args": [
                        "mcp-server-docker"
                    ]
                },
                "mcp-wsl": {
                    "command": "npx",
                    "args": ["-y", "mcp-wsl-exec"]
                },
                "mcp-compass": {
                    "command": "npx",
                    "args": [
                        "-y",
                        "@liuyoshio/mcp-compass"
                    ]
                },
                "ddg-search": {
                    "command": "uvx",
                    "args": ["duckduckgo-mcp-server"]
                },
                "calculator": {
                    "command": "uvx",
                    "args": ["mcp-server-calculator"]
                },
                "coingecko-mcp": {
                    "command": "npx",
                    "args": [
                        "mcp-remote",
                        "https://mcp.api.coingecko.com/sse"
                    ]
                },
                # "Context7": {
                #     "command": "npx",
                #     "args": ["-y", "@upstash/context7-mcp"]
                # },
                "webresearch": {
                    "command": "npx",
                    "args": ["-y", "@mzxrai/mcp-webresearch@latest"]
                }
            }

            selected_servers = {}

            if mcp_builtin_server:
                if isinstance(mcp_builtin_server, str):
                    mcp_builtin_server = [mcp_builtin_server]
                elif not isinstance(mcp_builtin_server, list):
                    raise ValueError(
                        "MCP_builtin_server must be a string or a list of strings")

                for name in mcp_builtin_server:
                    if name not in builtin_mcp_servers_list:
                        raise ValueError(
                            f"Unknown MCP built-in server: {name}")
                    selected_servers[name] = builtin_mcp_servers_list[name]

            if mcp_custom_server:
                selected_servers.update(load_custom_servers(mcp_custom_server))

            if not selected_servers:
                raise ValueError(
                    "At least one MCP server must be defined via built-in or custom configuration.")

            async def run_interactive():
                client = MCPClient(config={"mcpServers": selected_servers})

                agent_args = {
                    "llm": llm,
                    "client": client,
                    "max_steps": mcp_agent_max_steps,
                }
                if mcp_agent_system_prompt:
                    agent_args["system_prompt"] = mcp_agent_system_prompt

                agent = MCPAgent(**agent_args)

                def get_user_input():
                    if mcp_user_reply and mcp_user_reply.strip() != "":
                        return mcp_user_reply.strip()
                    try:
                        return input("Enter your reply → ").strip()
                    except EOFError:
                        return None

                if mcp_agent_chat:
                    print(
                        "\n=== Starting continuous MCP chat mode (type '(slash)exit', '(slash)quit', or '(slash)q' to quit) ===\n"
                    )
                    current_prompt = prompt
                    while True:
                        results = await agent.run(current_prompt)

                        if isinstance(results, list):
                            filtered_results = [
                                step for step in results
                                if not (isinstance(step, dict) and step.get("type") == "thinking")
                            ]
                        else:
                            # Wrap in list for consistency
                            filtered_results = [results]
                            return filtered_results
                        # for step in filtered_results:
                        #     print("\n=== Agent Output ===")
                        #     print(step)

                        # Wait for user input
                        while True:
                            user_reply = get_user_input()
                            if user_reply:
                                break
                            await asyncio.sleep(0.1)

                        if user_reply.lower() in ["\\exit", "\\quit", "\\q"]:
                            print("Exiting MCP chat mode.")
                            break

                        current_prompt = user_reply

                    return None
                else:
                    result = await agent.run(prompt)
                    # if isinstance(result, list):
                    #     for step in result:
                    #         print("\n=== Agent Output ===")
                    #         print(step)
                    # else:
                    #     print("\n=== Agent Output ===")
                    #     print(result)
                    return result

            return asyncio.run(run_interactive())
            # return await run_interactive()
        response = litellm.completion(**completion_args)
        if web == True:
            web_output = instance.search_tool(
                response.choices[0].message["content"])
            if instance.media == "":
                instance.final_prompt = f"""

You are a highly capable and intelligent assistant designed to deliver detailed, comprehensive, and accurate responses to complex queries. Your primary goal is to provide information that is factually correct, thoroughly analyzed, and tailored to address the query in its entirety, utilizing both your expertise and factual knowledge sourced from the web.

Your task is as follows:

Objective:
Analyze the provided query deeply and craft a detailed response using the most relevant and accurate information. You are also given additional insights and data sourced from the web to ensure your response is well-informed and enriched with context.

Requirements:
Query Analysis: Carefully evaluate the provided query to fully understand its scope, objectives, and nuances.
Web-Based Information Integration: Use the additional information sourced from the web, to strengthen your response. This information should complement your analysis and aid in constructing a factually robust and comprehensive answer.
Response Quality:
Ensure your response is exhaustive, addressing every aspect of the query comprehensively.
Your response should be structured and formatted for readability, using headings, subheadings, bullet points, and numbered lists where appropriate.
It should span more than 1000 words if required, delivering a level of depth and detail suitable for the complexity of the query.
Present information clearly, concisely, and in an easily digestible manner.
Avoid speculation, assumptions, or the inclusion of unrelated details. Stay focused on the query and the data provided.
Query:
The query to analyze is as follows:
"{prompt}"

Web-Based Supporting Information:
The following additional information has been sourced from the web and is provided to assist in crafting your response:
{web_output}

Guidelines for Response:
Comprehensive Coverage: Leave no relevant aspect of the query unaddressed. Explore all potential angles and provide an in-depth analysis to ensure completeness.
Clarity and Structure: Organize your response logically. Use headings and subheadings to create a clear hierarchy of information if needed. Provide summaries and highlight key insights for improved readability if needed.
Factually Accurate: Base your response strictly on factual information derived from your expertise and the content provided. Do not rely on assumptions or fabricate details.
High-Quality Content: Deliver information that is insightful, engaging, and reflects a thorough understanding of the topic. Focus on clarity and precision to ensure that the response is both accessible and authoritative.
When Information is Insufficient: If you determine that the available information (both your own and the web output) is insufficient to answer the query, respond with:
"I don't know."
Purpose:
Your response is intended to provide a rich, well-structured, and authoritative answer to the query, leaving no room for ambiguity or misinterpretation. Always prioritize accuracy, depth, and clarity."
    """

            if not instance.media == "":
                instance.final_prompt = f"""
        You are a highly capable assistant designed to extract and summarize information
        from multiple documents in various formats, such as DOCX, PPTX, PDF, TXT, Markdown, and others.

        The provided documents are as follows: {instance.media}

        Thoroughly analyze the content of these documents and generate a detailed response to the query below:
        "{prompt}"

        Here is some additional information from the web that will help you answer the query:{web_output}

        Only use factual information found within the documents to generate your response.
        Do not include assumptions or unrelated information in your output.

        If you feel that the provided documents do not contain enough information to answer the query,
        respond with "I don't know."

        Your response should be:
        1. Comprehensive and detailed, covering all relevant information.
        2. Well-structured and formatted, making it easy to read and understand.
        3. Contextual and concise where necessary, with clear references to the information extracted from the documents.

        Always ensure your output is factually accurate, verbose, and addresses the query fully.
        """
            if instance.final_prompt:
                content = [

                    {
                        "type": "text",
                        "text": instance.final_prompt
                    }
                ]
            else:
                content = [

                    {
                        "type": "text",
                        "text": prompt + " Here is additional information from the web that will help you to answer the query "+web_output
                    }
                ]

            if image:
                if not litellm.supports_vision(model):
                    raise AssertionError(
                        "The provided model does not support image(s) as an input!")

                if instance.media_ready == 1:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image}
                    })

                if instance.media_ready == 2:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": "data:image/jpeg;base64," + base64_image}
                    })

            completion_args = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            }

            if test_output:
                completion_args["mock_response"] = test_output

            response = litellm.completion(**completion_args)

        # Comming soon!
        # if mlops:
        #     time.sleep(1)
        # return response.choices[0].message['content']

        if instance.output_type == "voice":
            import pyttsx3
            engine = pyttsx3.init()

            engine.setProperty('rate', voice_speed)
            engine.setProperty('volume', voice_volume)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[voice_type].id)

            engine.save_to_file(
                response.choices[0].message["content"], voice_name)
            # engine.say(response.choices[0].message["content"])

            engine.runAndWait()
            return "Your output audio file is saved as " + voice_name
        else:
            return response.choices[0].message["content"]
