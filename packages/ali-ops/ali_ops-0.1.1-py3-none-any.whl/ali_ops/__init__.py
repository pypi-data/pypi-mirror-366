

import fire 
from config import CONFIG
from vpc import VPC 
from ecs import ECS 

class ENTRY(object):

  def __init__(self):
    self.vpc = VPC()
    self.config = CONFIG()
    self.ecs = ECS() 


def main() -> None:
    """Main function to run the CLI."""
    fire.Fire(ENTRY)

