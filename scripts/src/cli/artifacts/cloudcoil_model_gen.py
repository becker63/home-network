from __future__ import annotations
import logging
import sys
from concurrent.futures import Future, ProcessPoolExecutor, as_completed
from typing import Dict
from cloudcoil.codegen.generator import ModelConfig, generate
from configuration import CRD_SPECS, RemoteSchema, PROJECT_ROOT
from helpers.helpers import remove_path
from importlib.resources import files
from pathlib import Path

# Colored logging formatter
import os

class ColoredFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord):
        colors = [31, 32, 33, 34, 35, 36, 91, 92, 93, 94, 95, 96]
        # Hash process ID for unique coloring per process
        color_key = f"{os.getpid()}"
        color_code = colors[hash(color_key) % len(colors)]
        formatted_msg = super().format(record)
        return f"\033[{color_code}m{formatted_msg}\033[0m"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s - %(name)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logging.getLogger().handlers[0].setFormatter(ColoredFormatter("%(levelname)s - %(name)s - %(message)s"))

logger = logging.getLogger(__name__)

def generate_spec(spec: RemoteSchema) -> str:
    try:
        namespace: str = "src.ccgen." + spec.name
        config: ModelConfig = ModelConfig(
            namespace=namespace,
            input_=spec.urls,
            mode="resource",
            log_level="DEBUG",
            additional_datamodel_codegen_args=["--extra-fields", "allow"]
        )
        logger.info(f"Starting generation for {spec.name}")
        generate(config)
        logger.info(f"Completed generation for {spec.name}")
        return f"SUCCESS: {spec.name}"
    except Exception as e:
        error_msg: str = f"ERROR in {spec.name}: {e}"
        logger.error(error_msg)
        return f"ERROR: {spec.name} - {str(e)}"

def main():
    with ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
        specs_to_process = CRD_SPECS

        future_to_spec: Dict[Future[str], RemoteSchema] = {
            executor.submit(generate_spec, spec): spec
            for spec in specs_to_process
        }

        # Process results as they complete
        for future in as_completed(future_to_spec):
            spec: RemoteSchema = future_to_spec[future]
            try:
                result: str = future.result()
                logger.info(f"Result for {spec.name}: {result}")
                if result.startswith("ERROR:"):
                    logger.error("Stopping due to error")
                    executor.shutdown(wait=False, cancel_futures=True)
                    sys.exit(1)
            except Exception as e:
                logger.error(f"Exception for {spec.name}: {e}")
                executor.shutdown(wait=False, cancel_futures=True)
                sys.exit(1)

if __name__ == "__main__":
    remove_path(PROJECT_ROOT / "scripts" / "src" / "ccgen")

    (ccgen_root := PROJECT_ROOT / "scripts" / "src" / "ccgen").mkdir(parents=True, exist_ok=True)

    # dont ask wtf files is I have no idea
    tmpl_dir = Path(str(files("cloudcoil.codegen"))) / "templates" / "pydantic_v2"
    tmpl_dir.mkdir(parents=True, exist_ok=True)

    # Allow all extra fields my hacking around cloudcoils cookiecutter config
    (tmpl_dir / "ConfigDict.jinja2").write_text(
        '{% if extra_fields %}\nmodel_config = ConfigDict(extra="{{ extra_fields }}")\n{% endif %}\n'
    )

    (ccgen_root / "__init__.py").touch()
    main()
