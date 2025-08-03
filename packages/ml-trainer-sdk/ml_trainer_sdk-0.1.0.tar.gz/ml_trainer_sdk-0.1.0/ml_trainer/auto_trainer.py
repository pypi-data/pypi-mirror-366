from dataclasses import replace
from copy import deepcopy

from ml_trainer.config import DEFAULT_CONFIG, TrainingConfig, DatasetConfig # Ensure DatasetConfig is imported
from ml_trainer.tasks.task_registry import task_factory_registry



class AutoTrainer:
    def __init__(self, config: None, model=None, **kwargs): # Changed type hint to TrainingConfig
        self.config = deepcopy(DEFAULT_CONFIG)
        self.config.update(kwargs)

        if config:
            self.config.update(config)
        self.config.update(kwargs)

        self.task = self.config["task"]
        
        if self.task not in task_factory_registry:
            raise ValueError(
                f"Task: {self.task} is not registered\n"
                f"Available tasks: {list(task_factory_registry.keys())}"
            )
        
        factory = task_factory_registry[self.task]
        
        self.dataset = factory.create_dataset(self.config)
        # self.model = factory.create_model(self.config)
        self.model = model or factory.create_model(self.config)
        self.trainer = factory.create_trainer(self.model, self.dataset, self.config)

    def run(self):
        self.trainer.run()
