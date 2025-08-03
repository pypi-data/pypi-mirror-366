from pathlib import Path
from datetime import datetime
import hashlib
import httpx
import yaml
import json
import os
import zipfile
import tempfile

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.deep_crawling import BFSDeepCrawlStrategy
from crawl4ai.content_scraping_strategy import LXMLWebScrapingStrategy
from ..log import logger


async def download_docs(
    root_url: str,
    output_dir: str,
    max_depth: int = 1,
    include_external: bool = False,
):
    config = CrawlerRunConfig(
        deep_crawl_strategy=BFSDeepCrawlStrategy(
            max_depth=max_depth,
            include_external=include_external,
        ),
        scraping_strategy=LXMLWebScrapingStrategy(),
        verbose=True,
    )
    output_dir = Path(output_dir)
    if not output_dir.exists():
        output_dir.mkdir(parents=True)

    async with AsyncWebCrawler() as crawler:
        results = await crawler.arun(root_url, config=config)

        logger.info(f"Crawled {len(results)} pages in total")

        logger.info("Saving results to files...")
        for result in results:
            logger.info(f"URL: {result.url}")
            logger.info(f"Depth: {result.metadata.get('depth', 0)}")
            file_name = result.url.split("/")[-1].split("#")[0] + ".md"
            file_path = output_dir / file_name
            logger.info(f"Saving to {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                try:
                    f.write(result.markdown.raw_markdown)
                except Exception as e:
                    logger.error(e)


async def download_single_file(url: str, output_path: str):
    try:  
        async with httpx.AsyncClient() as client:  
            async with client.stream("GET", url) as response:  
                response.raise_for_status()  
                with open(output_path, "wb") as file:  
                    async for chunk in response.aiter_bytes():  
                        file.write(chunk)  
        logger.info(f"File downloaded to {output_path}")  
    except Exception as e:  
        logger.error(f"Failed to download file: {e}")  


def remove_duplicates(input_dir: str):
    # remove duplicates by text hash
    hashes = set()
    for file in Path(input_dir).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if hash in hashes:
                file.unlink()
            else:
                hashes.add(hash)


def remove_prefix(text: str, spliter="#"):
    prefix = text.split(spliter)[0]
    return text.replace(prefix, "")


def remove_prefix_from_files(dir: str, spliter="# "):
    for file in Path(dir).glob("*.md"):
        with open(file, "r", encoding="utf-8") as f:
            text = f.read()
            text = remove_prefix(text, spliter)
            with open(file, "w", encoding="utf-8") as f:
                f.write(text)


async def download_item(item: dict, output_dir: str | Path):
    dir = Path(output_dir)
    dir.mkdir(parents=True, exist_ok=True)
    if item["type"] in ["package documentation", "tutorial"]:
        await download_docs(item["url"], str(dir))
        remove_duplicates(str(dir))
        remove_prefix_from_files(str(dir))
    elif item["type"] == "github readme":
        await download_single_file(item["url"], dir / "README.md")
    else:
        logger.error(f"Unknown item type: {item['type']}")


async def build_vector_db(name: str, db_item: dict, output_dir: str):
    """Build a vector database from a database item(extracted from yaml file)

    Args:
        name: name of the database
        db_item: database item(extracted from yaml file)
        output_dir: output directory
    """
    from .vectordb import VectorDB
    # create database directory, dump metadata
    root_dir = Path(output_dir) / name
    root_dir.mkdir(parents=True, exist_ok=True)
    with open(root_dir / "metadata.yaml", "w", encoding="utf-8") as f:
        yaml.dump(db_item, f)

    # create vector database
    db = VectorDB(root_dir)

    # create info cache: record the success of each item
    info_cache_path = root_dir / "info_cache.json"
    if info_cache_path.exists():
        with open(info_cache_path, "r", encoding="utf-8") as f:
            info_cache = json.load(f)
    else:
        info_cache = {}

    for name, item in db_item["items"].items():
        try:
            download_success = False
            if info_cache.get(name, {}).get("success", False):
                logger.info(f"Item {name} already processed, skipping")
                continue
            docs_dir = root_dir / "raw" / name
            logger.info(f"Downloading item {name}")
            if (not docs_dir.exists()) or (not info_cache.get(name, {}).get("download_success", False)):
                await download_item(item, docs_dir)
                download_success = True
            # insert into database
            for file in docs_dir.glob("*.md"):
                logger.info(f"Inserting {file} from {name} into database")
                try:
                    await db.insert_from_file(file, {"source": name, "url": item["url"]})
                except Exception as e:
                    logger.error(f"Failed to insert file {file} from {name}: {e}")
                    continue
        except Exception as e:
            logger.error(f"Failed to process item {name}: {e}")
            info_cache[name] = {"success": False, "error": str(e), "download_success": download_success}
        info_cache[name] = {"success": True, "created_at": datetime.now().isoformat(), "download_success": download_success}

    # save info cache
    with open(info_cache_path, "w", encoding="utf-8") as f:
        json.dump(info_cache, f, indent=4)


async def build_all(yaml_path: str, output_dir: str):
    with open(yaml_path, "r", encoding="utf-8") as f:
        yaml_data = yaml.safe_load(f)

        for db_name in yaml_data:
            type_ = yaml_data[db_name]["type"]
            logger.info(f"Building {db_name} database")
            if type_ == "vector_db":
                await build_vector_db(db_name, yaml_data[db_name], output_dir)
            else:
                logger.error(f"Unsupported database type: {type_}")

    logger.info("Done")


async def upload_to_huggingface(output_dir: str, repo_id: str = "NaNg/pantheon_rag_db"):
    logger.info(f"Starting upload process for {output_dir} to {repo_id}")
    
    from huggingface_hub import login
    TOKEN = os.getenv("HUGGINGFACE_TOKEN")
    if not TOKEN:
        raise ValueError("HUGGINGFACE_TOKEN is not set")
    
    logger.info("Authenticating with Hugging Face...")
    login(TOKEN)
    from huggingface_hub import HfApi
    
    logger.info("Creating zip package...")
    # Create a temporary zip file
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = temp_zip.name
    
    # Create zip file with all contents from output_dir
    with zipfile.ZipFile(temp_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        output_path = Path(output_dir)
        file_count = 0
        for file_path in output_path.rglob('*'):
            if file_path.is_file():
                # Calculate relative path from output_dir
                relative_path = file_path.relative_to(output_path)
                zipf.write(file_path, relative_path)
                file_count += 1
                if file_count % 100 == 0:  # Log every 100 files
                    logger.info(f"Packed {file_count} files...")
    
    logger.info(f"Zip package created with {file_count} files. File size: {os.path.getsize(temp_zip_path) / (1024*1024):.2f} MB")
    
    try:
        logger.info(f"Uploading latest.zip to {repo_id}...")
        api = HfApi()
        api.upload_file(
            path_or_fileobj=temp_zip_path,
            path_in_repo="latest.zip",
            repo_id=repo_id,
            repo_type="dataset",
        )
        logger.info(f"Successfully uploaded {output_dir} as latest.zip to {repo_id}")
    finally:
        # Clean up temporary file
        logger.info("Cleaning up temporary files...")
        os.unlink(temp_zip_path)
        logger.info("Upload process completed")


async def download_from_huggingface(output_dir: str, repo_id: str = "NaNg/pantheon_rag_db", filename: str = "latest.zip"):
    """Download a zip file from Hugging Face and extract it to the specified directory
    
    Args:
        output_dir: Directory where the extracted files will be saved
        repo_id: Hugging Face repository ID, defaults to "NaNg/pantheon_rag_db"
        filename: Name of the file in the repo to download, defaults to "latest.zip"
    """
    logger.info(f"Starting download process from {repo_id}/{filename} to {output_dir}")
    
    from huggingface_hub import hf_hub_download
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create a temporary file for the downloaded zip
    with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as temp_zip:
        temp_zip_path = temp_zip.name
    
    try:
        logger.info(f"Downloading {filename} from {repo_id}...")
        # Download the zip file from Hugging Face
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            repo_type="dataset",
            local_dir=None,  # Let it use cache
        )
        
        # Copy to our temporary file (since hf_hub_download returns cache path)
        import shutil
        shutil.copy2(downloaded_path, temp_zip_path)
        
        file_size = os.path.getsize(temp_zip_path) / (1024*1024)
        logger.info(f"Downloaded {filename} ({file_size:.2f} MB)")
        
        logger.info(f"Extracting files to {output_dir}...")
        # Extract the zip file
        with zipfile.ZipFile(temp_zip_path, 'r') as zipf:
            file_list = zipf.namelist()
            logger.info(f"Extracting {len(file_list)} files...")
            
            extracted_count = 0
            for file_info in zipf.infolist():
                zipf.extract(file_info, output_path)
                extracted_count += 1
                if extracted_count % 100 == 0:  # Log every 100 files
                    logger.info(f"Extracted {extracted_count}/{len(file_list)} files...")
            
            logger.info(f"Successfully extracted {extracted_count} files to {output_dir}")
            
    except Exception as e:
        logger.error(f"Failed to download or extract files: {e}")
        raise
    finally:
        # Clean up temporary file
        logger.info("Cleaning up temporary files...")
        if os.path.exists(temp_zip_path):
            os.unlink(temp_zip_path)
        logger.info("Download process completed")

