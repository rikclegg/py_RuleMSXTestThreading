'''
Created on 28 Mar 2018

@author: metz
'''

import sched
import time
import logging
from rulemsx.rulemsx import RuleMSX
from rulemsx.ruleevaluator import RuleEvaluator
from rulemsx.action import Action
from rulemsx.datapointsource import DataPointSource
from rulemsx.rulecondition import RuleCondition


class RuleMSXTestThreading:
    
    def __init__(self):

        print("Initialising RuleMSX...")
        self.rulemsx = RuleMSX(logging.WARNING)
        print("RuleMSX initialised.")

        print("Create RuleSet...")
        self.build_rules()
        print("RuleSet ready.")

        print("Initialize DataSet...")
        self.create_dataset()
        print("Dataset Initialized.")
        
        print("Starting execution...")
        self.rulemsx.rulesets["demoRuleSet"].execute(self.rulemsx.datasets["demoDataSet"])
        print("Started execution.")

    def build_rules(self):
        
        print("Building Rules...")

        cond_test = RuleCondition("TestCondition", self.SecondsAtZero("CurrentTime"))

        action_show_dec_boundary = self.rulemsx.create_action("ShowDecBoundary", self.DisplayMessage("Seconds on Decimal Boundary: ", "BoundaryTime"))
        
        demo_ruleset = self.rulemsx.create_ruleset("demoRuleSet")

        rule_dec_boundary = demo_ruleset.add_rule("RuleDecBoundary")
        rule_dec_boundary.add_rule_condition(cond_test)
        rule_dec_boundary.add_action(action_show_dec_boundary)
        
        print("Rules built.")

    def create_dataset(self):
        
        demo_dataset = self.rulemsx.create_dataset("demoDataSet")
        
        demo_dataset.add_datapoint("CurrentTime", self.CurrentTime())
        demo_dataset.add_datapoint("BoundaryTime", self.SimpleInteger())

    class CurrentTime(DataPointSource):

        def __init__(self):

            self.timenow = 0

            self.s = sched.scheduler(time.time, time.sleep)
            self.s.enter(5, 1, self.set_time, (self.s,))
            self.s.run()

        def set_time(self, sc): 
            self.timenow = time.time()
            sc.enter(1, 1, self.set_time, (sc,))
            self.set_stale()
            
        def get_value(self):
            return self.timenow


    class SimpleInteger(DataPointSource):

        def __init__(self):

            self.int_value = 0

        def set_value(self, new_value): 
            self.int_value = new_value
            self.set_stale()
            
        def get_value(self):
            return self.int_value
        
    class SecondsAtZero(RuleEvaluator):
        
        def __init__(self, datapoint_name):
            
            self.datapoint_name = datapoint_name
            self.add_dependent_datapoint_name(datapoint_name)
        
        def evaluate(self,dataset):
            dp_value = dataset.datapoints[self.datapoint_name].get_value()

            if dp_value % 10:
                dataset.datapoints["BoundaryTime"].set_value(dp_value)
                return True
            else:    
                return False
            
    class DisplayMessage(Action):
    
        def execute(self, dataset):
                
            print("Second decimal boundary hit at: %d" % (dataset.datapoints["BoundaryTime"].get_value()))
                
                
if __name__ == '__main__':
    
    rt = RuleMSXTestThreading();
    
    input("Press any to terminate\n")

    print("Terminating...\n")

    rt.rulemsx.stop()
    
    quit()