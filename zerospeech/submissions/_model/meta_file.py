import re
from datetime import datetime
from pathlib import Path
from typing import Optional, Union, Dict, ClassVar, Literal

import yaml
from pydantic import BaseModel, AnyUrl, ValidationError

from zerospeech.misc import load_obj
from zerospeech.leaderboards import PublicationEntry
from .validation_context import ValidationContext

BenchmarkList = Literal[
    "prosAudit", "sLM21", "abxLS", "abx17", "tde17",
    "test-prosAudit", "test-sLM21", "test-abxLS", "test-abx17", "test-tde17",
]


def check_no_template(obj, root: str = "") -> ValidationContext:
    """ Check that object str fields do not have template values (in <,> tags)"""
    ctx = ValidationContext()
    if root:
        root = f"{root}."

    for key in obj.__fields__.keys():
        attr = getattr(obj, key)
        if isinstance(attr, str):
            ctx.error_assertion(
                re.match(r'<.*>', attr) is None,
                msg=f"{root}{key}: has value from template"
            )

    return ctx


class PublicationInfo(BaseModel):
    author_label: str = ""
    authors: str
    paper_title: Optional[str]
    paper_url: Optional[str]
    publication_year: int
    bib_reference: Optional[str]
    DOI: Optional[str]
    institution: str
    team: Optional[str]

    def get_validation(self) -> ValidationContext:
        """ Get Validation of PublicationInfo"""
        ctx = ValidationContext()

        # check no template
        ctx += check_no_template(self, root="publication")

        # publication.authors (required)
        ctx.error_assertion(
            self.authors is not None and len(self.authors) > 0,
            msg="publication.authors : was not found or empty"
        )

        # publication.authors (required)
        ctx.error_assertion(
            self.institution is not None and len(self.institution) > 0,
            msg="publication.institution : was not found or empty"
        )

        # publication.authors (required)
        ctx.error_assertion(
            self.publication_year is not None,
            msg="publication.publication_year : was not found or empty"
        )

        # publication.paper_title (recommended)
        ctx.warn_assertion(
            self.paper_title is not None and len(self.paper_title) > 0,
            msg="publication.paper_title : It is recommended to add the publication title "
        )

        # publication.paper_title (recommended)
        ctx.warn_assertion(
            self.paper_title is not None and len(self.paper_title) > 0,
            msg="publication.paper_title : It is recommended to add the publication title "
        )

        # publication.paper_title (recommended)
        ctx.warn_assertion(
            self.paper_url is not None and len(self.paper_url) > 0,
            msg="publication.paper_url : It is recommended to add the publication URL"
        )

        return ctx


class ModelInfo(BaseModel):
    model_id: Optional[str]
    system_description: str
    train_set: str
    gpu_budget: Optional[str]

    def get_validation(self) -> ValidationContext:
        """ Get Validation of ModelInfo"""
        ctx = ValidationContext()

        # check no template
        ctx += check_no_template(self, root="model_info")

        # model_info.system_description (required)
        ctx.error_assertion(
            self.system_description is not None and len(self.system_description) > 0,
            msg="model_info.system_description : was not found or empty"
        )

        # model_info.train_set (required)
        ctx.error_assertion(
            self.train_set is not None and len(self.train_set) > 0,
            msg="model_info.train_set : was not found or empty"
        )

        # model_info.gpu_budget (recommended)
        ctx.warn_assertion(
            self.gpu_budget is not None,
            msg="model_info.gpu_budget : It is recommended to add a GPU budget (GPU training time estimation)"
        )

        return ctx


class MetaFile(BaseModel):
    username: Optional[str]
    submission_id: Optional[str]
    benchmark_name: BenchmarkList
    model_info: ModelInfo
    publication: PublicationInfo
    open_source: bool
    code_url: Optional[Union[AnyUrl, str]]
    file_stem: ClassVar[str] = "meta.yaml"
    validation_context: ValidationContext = ValidationContext()

    class Config:
        arbitrary_types_allowed = True
        fields = {
            'validation_context': {'exclude': True},
            'file_stem': {'exclude': True}
        }

    @classmethod
    def from_file(cls, file: Path, enforce: bool = False):
        """ Load meta from object file (YAML, JSON, etc) """
        if not file.is_file() and not enforce:
            return None
        return cls.parse_obj(load_obj(file))

    @classmethod
    def to_template(cls, benchmark_name: BenchmarkList):
        return cls(
            username="<<auto-generated(str>): username on the zerospeech.com platform>",
            benchmark_name=benchmark_name,
            model_info=ModelInfo(
                model_id="<auto-generated>",
                system_description="<required(str): a description of the system>",
                train_set="<required(str): the dateset used to train the system>",
                gpu_budget="<optional(str): the number of gpu hours used to train the system>",
            ),
            publication=PublicationInfo(
                author_label="<required(str): a short label used for reference (ex: author1 et al.)>",
                authors="<required(str): the full names of the authors of the system (separated by commas)>",
                paper_title="<optional(str): the title of the paper referencing the system/submission>",
                paper_url="<optional(str): A URL referencing the paper online (arxiv.org or other)>",
                publication_year=datetime.now().year,
                institution="<required(str): name of the institution (University, company, etc..)>",
                team="<optional(str): name of the team>"
            ),
            open_source=True,
            code_url="<optional(str): a url to a github or other with the code used to create this system>"
        )

    def set_system_values(self, submission_location: Path, username: str, author_label: str):
        """ Update or set values managed by the submit system """
        self.username = username
        self.publication.author_label = author_label
        # write to file
        self.to_yaml(submission_location / self.file_stem, excluded=dict())

    def set_model_id(self, submission_location: Path, model_id: str):
        self.model_info.model_id = model_id
        # write to file
        self.to_yaml(submission_location / self.file_stem, excluded=dict())

    def set_submission_id(self, submission_location: Path, submission_id: str):
        self.submission_id = submission_id
        # write to file
        self.to_yaml(submission_location / self.file_stem, excluded=dict())

    def get_publication_info(self) -> PublicationEntry:
        pub = self.publication
        paper_ref = None
        if pub.authors and pub.paper_title:
            paper_ref = f"{pub.authors} ({pub.publication_year} {pub.paper_title})"

        return PublicationEntry(
            author_short=pub.author_label,
            authors=pub.authors,
            paper_title=pub.paper_title,
            paper_ref=paper_ref,
            bib_ref=pub.bib_reference,
            paper_url=pub.paper_url,
            pub_year=pub.publication_year,
            team_name=pub.team,
            institution=pub.institution,
            code=self.code_url,
            DOI=pub.DOI,
            open_science=self.open_source
        )

    def to_yaml(self, file: Path, excluded: Dict):
        with file.open("w") as fp:
            yaml.dump(dict(self._iter(to_dict=True, exclude=excluded)), fp)

    def is_valid(self) -> bool:
        """Check if meta.yaml has minimal values for submission """
        validation = ValidationContext()

        # check no template
        validation += check_no_template(self)

        # username (required)
        validation.error_assertion(
            self.username is not None and len(self.username) > 0,
            msg="Username is required"
        )

        # url (recommended)
        validation.warn_assertion(
            self.code_url is not None and len(self.code_url) > 0,
            msg="code_url : If possible we would appreciate a URL to the code of the system"
        )

        validation += self.model_info.get_validation()
        validation += self.publication.get_validation()
        validation.add_filename(filename=self.file_stem)

        self.validation_context = validation
        return not validation.fails()

    @classmethod
    def benchmark_from_submission(cls, location: Path) -> Optional[BenchmarkList]:
        """ Extract the benchmark name from a given submission """
        meta_file = location / cls.file_stem
        if not meta_file.is_file():
            return None

        with meta_file.open() as fp:
            meta_obj = yaml.load(fp, Loader=yaml.FullLoader)
        try:
            meta = cls.parse_obj(meta_obj)
            return meta.benchmark_name
        except ValidationError as e:
            print(e)
            return None
