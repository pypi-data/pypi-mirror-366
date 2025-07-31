"""
Template rendering helper module to provide "MANUAL_SECTION"
and template folder automatic searching and conversion
"""

import logging
import re
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Type, Union

from jinja2 import Environment, FileSystemLoader, StrictUndefined, Template


class TemplateRendererException(BaseException):
    """Specialization for TemplateRenderer related exception"""


class ManualSectionError(TemplateRendererException):
    """
    Raised when MANUAL SECTION validation failed
    """

    def __init__(self, message="MANUAL SECTION validation failed") -> None:
        self.message = message
        super().__init__(self.message)


def _remove_last_suffix(filename: str, extensions: Set[str]) -> str:
    """Remove last suffix if it matches one of the given extensions"""
    parts = filename.rsplit(".", 1)
    if len(parts) > 1 and parts[1] in extensions:
        return parts[0]
    return filename


class TemplateRenderer:
    """
    Template rendering helper class for Jinja2
    """

    MANUAL_SECTION_START = "MANUAL SECTION START"
    MANUAL_SECTION_END = "MANUAL SECTION END"
    MANUAL_SECTION_ID = "[a-zA-Z0-9_-]+"
    MANUAL_SECTION_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}: ({MANUAL_SECTION_ID}(?:\s|$))(.*?){MANUAL_SECTION_END}",
        re.DOTALL,
    )
    # patterns to validate sections
    MANUAL_SECTION_CHECK_PATTERN = re.compile(
        rf"{MANUAL_SECTION_START}.*?{MANUAL_SECTION_END}",
        re.DOTALL,
    )

    INJECTION_TAG_START = "<!--"
    INJECTION_TAG_END = "-->"
    INJECTION_PATTERN = (
        rf"{INJECTION_TAG_START} injection-pattern: (?P<name>[a-zA-Z0-9_-]+) {INJECTION_TAG_END}"
    )
    INJECTION_STRING_START = f"{INJECTION_TAG_START} injection-string-start {INJECTION_TAG_END}"
    INJECTION_STRING_END = f"{INJECTION_TAG_START} injection-string-end {INJECTION_TAG_END}"

    def __init__(self, data: Any, data_name: str = "") -> None:
        self._env = Environment(keep_trailing_newline=True, undefined=StrictUndefined)
        if not isinstance(data, dict) and not hasattr(data, "__dict__"):
            raise ValueError("Object or dictionary expected")
        self._data: Dict[str, Any] = {data_name: data} if data_name else data
        self.add_data({"raise_exception": self._raise_exception})

    def _raise_exception(self, message: str) -> None:
        """Raise exception with message"""
        raise TemplateRendererException(message)

    def _check_manual_section_ids(self, data_string: str, data_name: str) -> List[str]:
        """
        Check manual section ids for invalid or duplicated ids
        """
        possible_sections = self.MANUAL_SECTION_CHECK_PATTERN.findall(data_string)
        sections = self.MANUAL_SECTION_PATTERN.findall(data_string)
        if len(possible_sections) != len(sections):
            raise ManualSectionError(f"{data_name} has invalid section")
        sids = [sid for sid, _ in sections]
        # check for duplicates
        duplicates = {sid for sid in sids if sids.count(sid) > 1}
        if duplicates:
            raise ManualSectionError(f"{data_name} has duplicated id: {duplicates}")
        # return list of ids
        return sids

    def _check_manual_section_structure(self, data_string: str, data_name: str) -> None:
        """
        Check manual section structure for completeness and nesting
        """
        matches = self.MANUAL_SECTION_CHECK_PATTERN.findall(data_string)
        for section in matches:
            if (
                section.count(self.MANUAL_SECTION_START) > 1
                or section.count(self.MANUAL_SECTION_END) > 1
            ):
                raise ManualSectionError(f"Nested section in {data_name}: {section}")
        start_count = data_string.count(self.MANUAL_SECTION_START)
        end_count = data_string.count(self.MANUAL_SECTION_END)
        if start_count != end_count:
            raise ManualSectionError(
                f"Incomplete section in {data_name}: start={start_count}, end={end_count}"
            )

    def _validate_manual_sections(self, temp: str, rendered: str, prev_rendered: str) -> None:
        """
        Validate manual sections in template, current rendered and previously rendered
        """
        self._check_manual_section_structure(temp, "template")
        self._check_manual_section_structure(rendered, "rendered")
        curr_sids = self._check_manual_section_ids(rendered, "rendered")
        if prev_rendered:
            self._check_manual_section_structure(prev_rendered, "prev_rendered")
            prev_sids = self._check_manual_section_ids(prev_rendered, "prev_rendered")
            for sid in prev_sids:
                if sid not in curr_sids:
                    raise ManualSectionError(f"New template lost manual section: {sid}")

    def add_types(self, *custom_types: Union[Type, Callable]) -> None:
        """
        Add types as global variables to the Jinja environment
        This is useful to make enum variants accessible
        """
        type_map = {ty.__name__: ty for ty in custom_types}
        self._env.globals.update(type_map)

    def add_data(self, data: Dict[str, Any]) -> None:
        """
        Add dictionary data to the Jinja environment
        """
        self._env.globals.update(**data)

    def __render_from_string(self, template_path: Optional[Path], template_str: str) -> str:
        """Render template from string with filename set correctly in case of exception"""

        name = f'Inline template: "{template_str}"' if template_path is None else str(template_path)

        # copied from the implementation of `self._env.from_string(template_str)`
        global_vars = self._env.make_globals(None)
        template_class: Type[Template] = getattr(self._env, "template_class")
        template = template_class.from_code(
            self._env,
            self._env.compile(template_str, filename=name, name=name),
            global_vars,
            None,
        )

        return template.render(**self._data)

    def render_string(
        self,
        template_path: Optional[Path],
        temp: str,
        prev_rendered_string: str = "",
    ) -> str:
        """
        Render template string; preserve manual sections if they exist
        `template_path` is shown in the exception when Jinja2 fails. If it is `None`,
        the exception will instead print the entire template.
        """
        rendered_string = self.__render_from_string(template_path, temp)
        self._validate_manual_sections(temp, rendered_string, prev_rendered_string)
        if prev_rendered_string:
            manual_sections = self.MANUAL_SECTION_PATTERN.findall(prev_rendered_string)
            if manual_sections:
                for section_id, content in manual_sections:
                    section_pattern = re.compile(
                        rf"{self.MANUAL_SECTION_START}: {section_id}.*?{self.MANUAL_SECTION_END}",
                        re.DOTALL,
                    )
                    rendered_string = section_pattern.sub(
                        f"{self.MANUAL_SECTION_START}: {section_id}"
                        + content
                        + f"{self.MANUAL_SECTION_END}",
                        rendered_string,
                    )
        return rendered_string

    def inject_string(self, template_path: Path, temp: str, prev_rendered_string: str) -> str:
        """
        Render template & inject content to the previous rendered string
        """
        rendered_string = self.__render_from_string(template_path, temp)
        modifications = []

        for match in re.finditer(self.INJECTION_PATTERN, rendered_string):
            label = match.group("name")
            section_bodies = rendered_string[match.end() :].split(self.INJECTION_STRING_START)
            pattern_text = section_bodies[0].strip()
            # validate the regex pattern
            try:
                re.compile(pattern_text)
            except re.error as e:
                raise TemplateRendererException(
                    f"{template_path}, Invalid regex pattern '{pattern_text}': {e}"
                ) from e
            # validate if 'injection' named capture group exists
            if "(?P<injection>" not in pattern_text:
                raise TemplateRendererException(
                    f"{template_path}, Invalid regex pattern '{pattern_text}': "
                    "no 'injection' named capture group"
                )
            injection_string = section_bodies[1].split(self.INJECTION_STRING_END)[0]
            self._apply_injections(
                prev_rendered_string, pattern_text, injection_string, modifications
            )
            if not modifications:
                logging.warning("Failed to inject '%s':\n%s", label, pattern_text)

        return self._apply_modifications(prev_rendered_string, modifications)

    def _apply_injections(
        self,
        prev_rendered_string: str,
        pattern_text: str,
        injection_string: str,
        modifications: List[Any],
    ) -> None:
        """Apply injections based on the pattern and injection string"""
        for m in re.finditer(pattern_text, prev_rendered_string):
            injection_start = m.start("injection")
            injection_end = m.end("injection")
            modifications.append((injection_start, injection_end, injection_string))

    def _apply_modifications(self, prev_rendered_string: str, modifications: List[Any]) -> str:
        """Apply modifications to the previous rendered string"""
        modifications.sort(key=lambda x: x[0])
        modified_buffer = []
        last_pos = 0

        for injection_start, injection_end, injection_string in modifications:
            modified_buffer.append(prev_rendered_string[last_pos:injection_start])
            modified_buffer.append(injection_string)
            last_pos = injection_end

        # append the remaining part of the original string
        modified_buffer.append(prev_rendered_string[last_pos:])

        return "".join(modified_buffer)

    def render_file(self, temp_filepath: Union[Path, str], prev_rendered_string: str = "") -> str:
        """
        Render template with given template file path; preserve manual sections if they exist
        """
        if not isinstance(temp_filepath, Path):
            temp_filepath = Path(temp_filepath)
        with temp_filepath.open(mode="r", encoding="utf-8") as temp_file:
            temp_string = temp_file.read()
            rendered_string = self.render_string(temp_filepath, temp_string, prev_rendered_string)
        return rendered_string

    def _is_text_file(self, filepath: Path) -> bool:
        """Check if the file is a text file"""
        try:
            filepath.read_text(encoding="utf-8")
            return True
        except (UnicodeDecodeError, IOError):
            return False

    def generate_file(
        self,
        temp_filepath: Union[Path, str],
        output_filepath: Union[Path, str],
        only_template_files: bool = True,
    ) -> None:
        """
        Render the given temp_filepath and generate the output file with the given out_filepath
        - Trick to skip generation with empty filename ("");
          for example with the below template filename, the generation of file can be skipped
          when `temp_data.has_interface` is `false`.
          {{"interface" if temp_data.has_interface else ""}}.hpp.j2
        """
        temp_filepath = (
            Path(temp_filepath) if not isinstance(temp_filepath, Path) else temp_filepath
        )
        output_filepath = (
            Path(output_filepath) if not isinstance(output_filepath, Path) else output_filepath
        )

        output_filename = output_filepath.stem
        if not output_filename or not self._is_text_file(temp_filepath):
            return

        temp_string = self._read_file(temp_filepath)
        self._env.loader = FileSystemLoader(temp_filepath.parent)
        prev_rendered_string = self._read_file(output_filepath) if output_filepath.exists() else ""

        if temp_filepath.suffix == ".inj":
            if not prev_rendered_string:
                raise TemplateRendererException(f"{output_filepath} is required for injection")
            rendered_string = self.inject_string(temp_filepath, temp_string, prev_rendered_string)
        elif temp_filepath.suffix != ".j2" and only_template_files:
            rendered_string = temp_string
        else:
            rendered_string = self.render_string(temp_filepath, temp_string, prev_rendered_string)

        output_filepath.parent.mkdir(parents=True, exist_ok=True)
        self._write_file(output_filepath, rendered_string)
        logging.info("=> %s generated!", output_filepath)

    def _read_file(self, filepath: Path) -> str:
        """Read the content of a file"""
        if filepath.exists():
            with filepath.open(mode="r", encoding="utf-8") as file:
                return file.read()
        return ""

    def _write_file(self, filepath: Path, content: str) -> None:
        """Write content to a file"""
        with filepath.open(mode="w", encoding="utf-8") as file:
            file.write(content)

    def generate(
        self,
        temp_path: Union[Path, str],
        output_dir: Union[Path, str],
        only_template_files: bool = True,
    ) -> None:
        """
        Main function to render template files and to generate output files
        """
        if not isinstance(temp_path, Path):
            temp_path = Path(temp_path)
        if not isinstance(output_dir, Path):
            output_dir = Path(output_dir)

        if temp_path.exists():
            if temp_path.is_file():
                output_filename = _remove_last_suffix(
                    self.render_string(None, temp_path.name), {"j2", "inj"}
                )
                if output_filename:
                    output_filepath = output_dir / output_filename
                    self.generate_file(temp_path, output_filepath, only_template_files)
            elif temp_path.is_dir():
                filename_pattern = "*"
                temp_files = [file for file in temp_path.rglob(filename_pattern) if file.is_file()]
                for temp_filepath in temp_files:
                    # render folder or file name in Path and remove j2 suffix
                    output_filename = _remove_last_suffix(
                        self.render_string(None, temp_filepath.name), {"j2", "inj"}
                    )
                    if output_filename:
                        output_filepath = Path(
                            _remove_last_suffix(
                                self.render_string(None, str(temp_filepath)),
                                {"j2", "inj"},
                            )
                        )
                        output_filepath = output_dir / output_filepath.relative_to(temp_path)
                        self.generate_file(temp_filepath, output_filepath, only_template_files)
        else:
            raise FileNotFoundError(f"File not found: {temp_path}")
