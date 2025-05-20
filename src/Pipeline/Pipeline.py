from typing import List, Union, Optional, Tuple
from itertools import product
from tqdm import tqdm

from src.Pipeline.PipelineStep import PipelineStep
from src.Pipeline.ExceptionPolicy import ExceptionPolicy
from src.Pipeline.ExecutionPolicy import ExecutionPolicy
from src.DB import PipelineGrade, Component
from src.Pipeline.Grader import Grade
from beanie.operators import Set


class Pipeline:
    def __init__(
        self,
        pipeline_type: str,
        steps: Optional[List[Union[PipelineStep, List[PipelineStep]]]] = None,
        grader: Optional[callable] = None,
        save_results: bool = True
    ):
        self.pipeline_type = pipeline_type
        self.steps: List[List[PipelineStep]] = [
            step if isinstance(step, list) else [step]
            for step in (steps or [])
        ]
        self.grader = grader
        self.write_results = save_results

    def add_step(
        self,
        step: Union[PipelineStep, List[PipelineStep]],
        exception_policy: Optional[ExceptionPolicy] = None,
        execution_policy: ExecutionPolicy = None
    ):
        step_list = step if isinstance(step, list) else [step]
        for s in step_list:
            if exception_policy:
                s.exception_policy = exception_policy
            if execution_policy:
                s.execution_policy = execution_policy
        self.steps.append(step_list)

    async def __call__(
        self,
        components: List[Component],
        parallel: bool = True,
        exception_policy: ExceptionPolicy = ExceptionPolicy.TRY,
        execution_policy: ExecutionPolicy = ExecutionPolicy.CACHE
    ) -> Tuple[Optional[List[Grade]], List[List[Tuple]]]:
        inputs = [[(comp, comp) for comp in components]]
        num_components = len(components)
        for multistep in self.steps:
            next_inputs = []
            for step in multistep:
                print(f"Running step: {step._step_key}")
                # Apply the current 'step' to each list in the current 'inputs'
                for single_input_list in inputs:
                    current_step_output_list = []
                    for x, c in tqdm(single_input_list, desc="Processing", unit="step", total=len(single_input_list)):
                        if x is None:
                            current_step_output_list.append((None, c))
                            continue
                        res, updated_c = await step(x, c, exception_policy=exception_policy, execution_policy=execution_policy)
                        current_step_output_list.append((res, updated_c))
                    # After processing one single_input_list with the current step, add the result list to next_inputs
                    next_inputs.append(current_step_output_list)
                    # Offload resources after step completion
                    step.offload_resources()
            # After processing all steps in the multistep, update inputs for the next iteration
            inputs = next_inputs

        if self.grader:
            gradings = []
            for single_input in inputs:
                print("Single_input:", type(single_input))
                print("Single_input_0", type(single_input[0]))
                print("Single_input_0_0", type(single_input[0][0]))
                print("Single_input_0_1", type(single_input[0][1]))
                grading = self.grader(single_input)
                gradings.append(grading)
            if self.write_results:
                await self.save_results(gradings)
            return gradings, inputs
        return None, inputs

    async def save_results(self, gradings: List[Grade]):
        step_keys = [[step._step_key for step in multistep] for multistep in self.steps]
        display_names = [[step.get_display_name() for step in multistep] for multistep in self.steps]

        combined_keys = ["_".join(combo) for combo in product(*step_keys)]
        combined_display = list(product(*display_names))
        combined_steps = list(product(*step_keys))

        for grading, key, step_list, display_list in zip(gradings, combined_keys, combined_steps, combined_display):
            print(f"Saving results for key: {key}")
            print(step_list)
            print(display_list)
            print("*" * 20)
            await PipelineGrade.find_one(PipelineGrade.key == key).upsert(
                Set({**grading.model_dump(), "steps": step_list}),
                on_insert=PipelineGrade(
                    key=key,
                    steps=step_list,
                    pipeline_type=self.pipeline_type,
                    display_steps=display_list,
                    **grading.model_dump()
                )
            )

    def __str__(self):
        lines = [f"{i+1}: {step}" for i, step in enumerate(self.steps)]
        return f"Pipeline with {len(self.steps)} steps:\n" + "\n".join(lines)
