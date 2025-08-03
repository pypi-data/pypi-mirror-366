class PowerPlan:
    name: str
    id: str    
    enabled: bool
    dynamic_properties: list[any]
    
    def __init__(self, name: str, id: str, enabled: bool, dynamic_properties: list[any]):
        self.name = name
        self.id = id
        self.enabled = enabled
        self.dynamic_properties = dynamic_properties
        
    