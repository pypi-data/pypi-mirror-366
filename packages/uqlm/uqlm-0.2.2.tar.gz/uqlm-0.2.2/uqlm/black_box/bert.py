# Copyright 2025 CVS Health and/or one of its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import bert_score
import numpy as np
from typing import List, Optional

from uqlm.black_box.baseclass.similarity_scorer import SimilarityScorer

import time
from rich.progress import Progress


class BertScorer(SimilarityScorer):
    def __init__(self) -> None:
        """
        Class for computing BERTScore values between original responses and candidates. For more on
        BERTScore, refer to Zhang et al.(2020) :footcite:`zhang2020bertscoreevaluatingtextgeneration`.
        """
        from transformers import logging

        logging.set_verbosity_error()

    def evaluate(self, responses: List[str], sampled_responses: List[List[str]], progress_bar: Optional[Progress] = None) -> List[float]:
        """
        This method computes model-based text similarity metrics values for the provided pairs of texts.

        Parameters
        ----------
        responses : list of strings
            Original LLM response

        sampled_responses : list of list of strings
            Candidate responses to be compared to the original response

        progress_bar : rich.progress.Progress, default=None
            If provided, displays a progress bar while scoring responses

        Returns
        -------
        List of float
            Mean BertScore values
        """
        if progress_bar:
            progress_task = progress_bar.add_task("  - [black]Scoring responses with BERTScore...", total=len(responses))
        results = []
        for i in range(len(responses)):
            score = self._compute_score(response=responses[i], candidates=sampled_responses[i])
            results.append(score)
            if progress_bar:
                progress_bar.update(progress_task, advance=1)
        time.sleep(0.1)
        return results

    @staticmethod
    def _compute_score(response: str, candidates: List[str]) -> float:
        """Compute mean BERTScore between a response and candidate responses"""
        num_responses = len(candidates)
        duplicated_response = [response] * num_responses
        P, R, F1 = bert_score.score(list(duplicated_response), refs=list(candidates), lang="en", verbose=False, batch_size=num_responses)
        return np.mean([float(f) for f in F1])
