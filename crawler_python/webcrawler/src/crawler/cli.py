

import argparse
import os


from .main import crawler,crawl_deep


class EnvDefault(argparse.Action):
    """
    Clase para permitir que un argumento tome un valor por defecto
    desde la variable de entorno indicada en 'envvar'.
    """
    def __init__(self, envvar=None, required=True, default=None, *args, **kwargs):
        
        
        if envvar is not None and envvar in os.environ:
            default = os.environ[envvar]
            required = False

        
        if "envvar" in kwargs:
            del kwargs["envvar"]

        super().__init__(default=default, required=required, *args, **kwargs)
        
        self.envvar = envvar  

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)


def main():
    parser = argparse.ArgumentParser(description="CLI for FIFA Crawler.")

    parser.add_argument(
        "--crawler-type",
        choices=["shallow", "deep"],
        default="shallow",
        help="Select 'shallow' to crawl only the main URL, or 'deep' to recursively crawl discovered URLs."
    )
    
    parser.add_argument(
        "--max-depth",
        type=int,
        default=1,
        help="Maximum depth to crawl for 'deep' crawling (default=1)."
    )

    parser.add_argument(
        "--url",
        default="https://www.google.com",
        help="URL to start the crawler"
    )

    
    parser.add_argument(
        "--api-key",
        action=EnvDefault,
        envvar="MISTRAL_API_KEY",
        required=True,
        help="Mistral AI API key (env variable MISTRAL_API_KEY)."
    )

    
    parser.add_argument(
        "--output-file",
        default="crawler.md",
        help="Name and extension of output file (.md, .txt, .json)"
    )

    
    parser.add_argument(
        "--ai-prompt",
        default="Write a concise summary of the following",
        help="Prompt for the AI agent to extract the desired information."
    )

    args = parser.parse_args()

    
    if args.api_key:
        os.environ["MISTRAL_API_KEY"] = args.api_key

    
    if args.crawler_type == "shallow":
        list_urls = crawler(
            url=args.url,
            output_file=args.output_file,
            ai_prompt=args.ai_prompt
        )
    elif args.crawler_type == "deep":
       
        list_urls = crawl_deep(
            start_url=args.url,
            output_file=args.output_file,
            ai_prompt=args.ai_prompt,
            max_depth=args.max_depth
        )
    else:
        # Omitir esta parte si tu 'choices' ya valida las opciones
        print(f"Unknown crawler type '{args.crawler_type}'")

    print("URL base procesada:", args.url)
    print("Total de URLs encontradas:", len(list_urls))


if __name__ == "__main__":
    main()
