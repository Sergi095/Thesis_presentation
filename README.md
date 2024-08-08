# MSc Thesis Presentation: Sensory Heterogeneous Predator Swarm vs Fully Sensing Prey Swarm

This presentation is made with Dash and it is deployed on a free hosting service. The presentation can be found at [Link](https://sergi095.pythonanywhere.com/0).

There is a small playground where you can run a small 2D simulation of preys and predators, but since it is hosted on a free web service, the simulation will run slow 😞. Therefore, the best is to run the app locally and see how it works.


### Anaconda
To run the app first you need to create an evironment. Here's how to do it with Anaconda.

```bash
$ conda create --name myenv
$ conda activate myenv
```
Then clone this repository:

```bash
$ git clone https://github.com/Sergi095/Thesis_presentation.git
$ cd Thesis_presentation
$ pip install -r requirements.txt # install the dependencies.
```


### Without Anaconda
You can also create a virtual environment with python. 

First, clone this repository
```bash
$ git clone https://github.com/Sergi095/Thesis_presentation.git
$ cd Thesis_presentation
$ python3 -m venv myenv # create an environment inside the repository
$ source myenv/bin/activate # activate it.
$ pip install -r requirements.txt # install the dependencies.
```


### Running the app

To run the app just do:

```bash
(myenv) $ python app.py
```

This will create a running app on localhost: http://127.0.0.1:8050/

Then you can play with the simulation 😃.

