# dots-infrastructure
This package provides the infrastructure to develop dots calculation services an example of how a calculation function can be developed can be found in the [Dots calculation service template](https://github.com/dots-energy/Dots-calculation-service-template). This package implements [helics](https://helics.org/) as a co-simulation engine. 

## Contents
- Federate structure
- Publication/subscription
- Threading

### Federate structure
When defining a calculation service you have to create a python class that inherits from `HelicsSimulationExecutor`. This class will have the necesairy functions to define a calculation service. To add new calculations to a calculation service use the `add_calculation` of the `HelicsSimulationExecutor` class. This will instantiate a new instance of the `HelicsFederateExecutor` class which is responsible for the life cycle of a helics federate. To clarify please refer to the class diagram below:

![dots component diagram](./docs/images/federate-structure.png)

Once all calculations are defined, initiate the newly created subtype of `HelicsSimulationExecutor` and call upon the `start_simulation` function. This will start up the helics federates that will be part of the co-simulations federation. Each calculation within a calculation service will be handled by a seperate helics federate.

### Publication/subscription
One of the major features of this package is managing the publications and subscriptions of a calculation service. Publications and subscriptions types are defined by the calculation service itself and are coupled to the simulation's esdl file. What is important to consider here is that a calculation service simulates multiple instances of the same esdl type. Hence, calculation services are defined as a simulator for a specific esdl type. The simulation's esdl file determines which publication the calculation service will subscribe to. 

Consider an esdl file that has a house that is connected to two pv panels and a seperate pv panel that is not connected to anything. See the below description of the topology:
```
pv panel (id:1) -- House (id: 1) -- pv panel (id: 2)

pv panel (id: 3)
```

Now take the calculation service that is developed for the house. This service might want the output of the pv panel calculation services connected to it. As long as the house service specifies that it needs input from the pv panels the package will make sure the house service subscribes to the output of pv panels with id 1 and id 2. The subscription key will look like: `PVPanel/{Outputname}/{PVPanelId}`. When all the inputs for a calculation service have been received the calculation service' calculation function will be called with the new input values in the form of a dictionary.

The house calculation service might also want to output values to different calulation services. As long as the house calculation service specifies that the service outputs specific values the publications will be registered within the helics federation and other calculation services might subscribe to it. The publication key will be similar to the example of the subscription key.

Finally, as mentioned earlier a calculation service might simulate multiple instances of the same esdl type. So lets consider a calculation service for the pv panels in the above example. The associated calculation functions will be called three times in a single time step by this infrastructure package because there are three pv panels. Each call to the calculation functions has different parameters that are unique to the single instance of a pv panel.

### Threading
When defining calculations for a calculation service it is important to know how threading is taken care of in this package. Each calculation might have a specific helics execution period (or frequency) and corresponding offset. Therefore, in order for helics to properly scedule the different calculations of a calculation service each calculation is handled by a seperate helics federate that is running on a sperate thread.
