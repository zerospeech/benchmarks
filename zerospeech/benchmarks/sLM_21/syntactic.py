from .data_model import SLM21Task, SLM21Submission, SLM21Dataset


# todo implement syntactic task
class SyntacticTask(SLM21Task):
    _name = "syntactic"

    def eval(self, submission: SLM21Submission, dataset: SLM21Dataset):
        pass
