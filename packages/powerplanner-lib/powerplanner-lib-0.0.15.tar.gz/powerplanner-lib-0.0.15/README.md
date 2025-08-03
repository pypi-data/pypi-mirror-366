# PowerPlanner API Lib
Library to support accessing the powerplanner API
Mainly used for the Home assistant integration

### Create an instance with your api key from powerplanner

#### update()
Fetches all schedules from the powerplanner API and returns the raw json result

If there is removed or added plans these will be available in the "new_plans" & "old_plans" variable
The "plans_changed" variable will also be true.

#### toggle(plan_id: str, enabled:bool)
Enables or disables a plan and updates the schedules

#### set_property(plan_id: str, property_key: str, value: any)
Updates a dynamic rule value on a plan

#### get_next_change(name: str)
returns when a plan will change its enabled status

#### add_sensor(sensor)
Adds a sensor to the collection and triggers the assigned callback

#### remove_sensor(sensor_name: str)
Removes a sensor from the collection

#### time_to_change(name: str)
Returns how many seconds left it is before the plan changes status

#### is_on(name: str)
Returns the current status for a plan by checking the schedule

#### authenticate():
Checks if the api key is correct
