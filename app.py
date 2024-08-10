import dash
from dash import dcc, html, Input, Output, State
import dash_katex
from typing import Tuple, List
from sim import PredatorPreySimulation
import plotly.graph_objs as go
# import plotly.express as px
# import pandas as pd
import numpy as np
# Initialize the Dash app
app = dash.Dash(__name__, title='Thesis Presentation', suppress_callback_exceptions=True)
server = app.server
app.tile = "Thesis Presentation"
# app.favicon = "assets/icon.ico"
# VU_logo_RGB-01.jpg

# Sample slide definitions
slides = [
    # {
    #     "title": "By Sergio A. Gutierrez Maury",
    #     "content": [

    #         html.Div([
    #             dcc.Markdown(r'''
    #             ### Outline
    #             - Introduction
    #             - Related Work
    #             - Methods
    #             - Experimental Setup
    #             - Results
    #             - Discussion
    #             - Conclusions
    #             ''', mathjax=True, style={'fontSize': '1.2vw'}),
    #         # html.Div([
    #             html.Img(src="assets/2Dfast.gif", style={'maxWidth': '20vw', 'maxHeight': '40vh', 'display': 'block','margin': '-0 auto', 'marginBottom': '10px'}),
    #             html.Img(src="assets/pybulletFast.gif", style={'maxWidth': '20vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginTop': '10px'})
    #         # ], style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'justifyContent': 'right', 'alignItems': 'right'})
            
    #         ], style={'flex': '1', 'padding': '10px'}),
    #         html.Div([
    #             dcc.Markdown(r'''
    #             ### Project Code
    #             [Github Code](https://github.com/Sergi095/Vu_Thesis_Prey_Predator.git)
    #             ''', mathjax=True, style={'fontSize': '1.2vw', 'alignItems':'center'}),
    #             ], style={'flex': '1', 'padding': '10px', 'alignItems': 'center'}),
    #         # html.Div([
    #             # html.Img(src="assets/2Dfast.gif", style={'maxWidth': '30vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginRight': '10px'}),
    #             # html.Img(src="assets/pybulletFast.gif", style={'maxWidth': '30vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginLeft': '10px'})
    #         # ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center'})
    #     ]
    # },
{
    "title": html.A("By Sergio A. Gutierrez Maury", href="https://github.com/Sergi095", style={'textDecoration': 'none', 'color': 'inherit'}),
    "content": [
        html.Div([
            html.Div([
                dcc.Markdown(r'''
                ### Outline
                - [Introduction](/1)
                - [Related Work](/2)
                - [Methods](/3)
                - [Experimental Setup](/6)
                - [Results](/7)
                - [Discussion](/10)
                - [Conclusions](/12)
                ''', mathjax=True, style={'fontSize': '1.2vw'}),
            ], style={'flex': '1', 'padding': '10px'}),
            html.Div([
                html.Img(src="assets/2Dfast.gif", style={'maxWidth': '25vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginRight': '10px'}),
                html.Img(src="assets/pybulletFast.gif", style={'maxWidth': '25vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginLeft': '10px'})
            ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'flex-start', 'alignItems': 'flex-end'})
        ], style={'display': 'flex', 'flexDirection': 'row'}),
        html.Div([
            html.Div([
                dcc.Markdown(r'''
                ### Project Code
                ''', mathjax=True, style={'fontSize': '1.2vw', 'alignItems':'center'}),
                html.A([
                    html.Img(src="assets/GitHub_logo.png", style={'maxWidth': '20px', 'maxHeight': '20px', 'marginRight': '5px'}),
                    "Github Repository"
                ], href="https://github.com/Sergi095/Vu_Thesis_Prey_Predator.git", style={'textDecoration': 'none', 'fontSize': '1.2vw', 'alignItems': 'center'}),
                html.A([
                    html.Button('Download Presentation as PDF', id='download-pdf', n_clicks=0, style={'padding': '1vh', 'fontSize': '1.2vw', 'marginLeft': '10px', "pointer": "cursor"})
                ], href="/assets/presentation.pdf", download="presentation.pdf", style={'textDecoration': 'none', 'fontSize': '1.2vw', 'alignItems': 'center'})
            ], style={'flex': '1', 'padding': '10px', 'alignItems': 'center'}),
            html.Div([
                dcc.Markdown(r'''
                ### Playground 
                At slide [13](/13) you can interact with the simulation.
                ''', mathjax=True, style={'fontSize': '1.2vw', 'textAlign': 'right'}),
            ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'justifyContent': 'flex-end'}),
        ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'space-between', 'alignItems': 'center'}),
    ]
},
    {
        "title": "Introduction",
        "content": [
            html.Div([
                dcc.Markdown(r'''

                - The dynamics between prey and predators have been extensively studied across fields like mathematics, robotics, and biology.
                  These studies help us understand population dynamics, migrations, and species adaptation.
                  In multi-agent environments, both predators and prey may evolve swarming behaviors for escape or chase strategies. \[[2-5](/15)\]

                - Predators often hunt collectively to capture challenging prey, despite the cost of sharing.
                  Examples include lions, hyenas, wolves, and killer whales.
                  Their hunting strategies vary significantly, utilizing senses like sight, smell, and echolocation. \[[6-9](/15)\]

                - Prey develop swarming behaviors to increase survival chances, such as confusing predators.
                 Examples include pigeons and fish, which exhibit complex escape patterns through self-organization and group behaviors. \[[10-13](/15)\]

                - Inspired by these natural behaviors, researchers have developed swarm robotic systems to mimic these interactions for complex tasks.
                  This study explores mechanisms like Distance Modulation (DM) and Attractive Distance Modulation (ADM) in a dynamic environment. \[[15](/15)\]
                ''', mathjax=True, style={'fontSize': '1.5vw'})
            ], style={'flex': '1', 'padding': '10px'})
        ]
    },
    {
        "title": "Related Work",
        "content": [
            html.Div([
                dcc.Markdown(r'''

                - Reinforcement Learning Approaches: Studies integrating Reinforcement Learning (RL) with flocking control to model predator-prey interactions, showing improved learning efficiency and coordination. \[[16-18](/15)\]

                - Mathematical Models and Theoretical Analysis: Development of minimal models and particle-based approaches to study predator-swarm dynamics, revealing various interaction patterns like escape, confusion, and capture. \[[19-20](/15)\]

                - Applications and Practical Implementations: Use of prey-predator algorithms in real-world scenarios such as surveillance and herding with autonomous drones, demonstrating the practical utility of swarm robotics. \[[21-22](/15)\]

                - Swarm Robotics and Flocking Behavior: Research on RAOI behavior policies and prey-predator tasks to enhance cooperative behavior and efficiency in robotic swarms. \[[23-25](/15)\]
                ''', mathjax=True, style={'fontSize': '1.5vw'})
            ], style={'flex': '1', 'padding': '10px'})
        ]
    },

    {
        "title": "Methods: Proximal Control Vectors",
        "content": [
            dcc.Markdown(r'''
            Following the methodology of “Collective Gradient Following with Sensory Heterogeneous UAV Swarm” \[[1](/15)\] I implement two different proximal control vectors:
            - Attractive Distance Modulation (ADM)
            - Distance Modulation (DM or Normal P-vector)

            The formula for the normal P-vector is given by:
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''


            $p_i^m(d_i^m, \sigma_i)=-\epsilon \cdot \left[ 2 \cdot \frac{\sigma_i^4}{(d_i^m)^5} - \frac{\sigma_i^2}{(d_i^m)^3} \right]$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r''' The formula for ADM is given by: ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''
            $p_i^m(d_i^m, \sigma_i)=-\epsilon \cdot \left[\frac{\sigma_i}{(d_i^m)} - \sqrt{\frac{\sigma_i}{(d_i^m)}} \right]$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            html.Div([
                html.Img(src="assets/p_vectors.png", style={'maxWidth': '35vw', 'maxHeight': '300px', 'display': 'block', 'margin': '0 auto'})
            ], style={'textAlign': 'center'}),
            dcc.Markdown(r'''
            The plot show the repulsive and attractive forces for both methods.

            The equlibrium point is at $d_{des}^i= \sqrt{2} \cdot \sigma_i$ for DM and $d_{des}^i= \sigma_i$ for ADM.
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'})
        ]
    },
    {
        "title": "Methods: Predator Swarm",
        "content": [
            dcc.Markdown(r'''
            The flocking control for predators is either Normal P-vector or ADM. The predators do not use alignment control, and the force formula is as follows:
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''
            $force=\alpha \cdot \vec{p}$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r'''
            Predators are able to chase preys with minimal information possible, which is the distance.
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            html.Div([
                html.Img(src="assets/predator_prey_distance_speed_up.gif", style={'maxWidth': '40vw', 'maxHeight': '300px', 'display': 'block', 'margin': '0 auto'})
            ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '10px'}),
            dcc.Markdown(r'''
            The way this mechanism is implemented is by taking all distances within a sensed range, averaging them, then the reciprocal is added to the desired distance as follows:
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''
            $\sigma_i=\frac{1}{distance} + \sigma_c$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r'''
            where sigma constant is a parameters that controls for upper and lower bounds of the desired distance, and the resulting $\sigma_i$ is the desired distance modulation.

            Furthermore, there are non-sensing agents in the predator swarms, which means they maintain a constant sigma.
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'})
        ]
    },
    {
        "title": "Methods: Prey Swarm",
        "content": [
            dcc.Markdown(r'''
            The prey’s flocking is controlled solely by the Normal P vector. I am not implementing ADM on preys. Furthermore, the preys use a repulsion vector to run away from sensed predators.
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''
            $force=\alpha \cdot \vec{p} + \kappa \cdot \vec{rp}$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r'''
            The repulsion vector is calculated as follows:
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            dcc.Markdown(r'''
            $\vec{rp}_{prey_{i}}=\vec{pos}_{prey_{i}} - \vec{avgPos}_{predators}$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r'''
            Where each individual prey's repulsion is computed by first computing the average position of predators and subtracting that point from the prey's position, such that it can run in the opposite direction.
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'left'}),
            html.Div([
                html.Img(src="assets/predator_prey_repulsion_fast2.gif", style={'maxWidth': '30vw', 'maxHeight': '250px', 'display': 'block', 'margin': '0 auto'}),
                html.Img(src="assets/kappaPREDSdist.png", style={'maxWidth': '30vw', 'maxHeight': '300px', 'display': 'block', 'margin': '0 auto'})
            ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center', 'gap': '10px', 'overflow': '0 auto'}),
          dcc.Markdown(r'''
            Kappa is the multiplier of the repulsion vector, which takes the following form:''', mathjax=True, style={'fontSize': '1.5vw'}),
            dcc.Markdown(r'''
            $\kappa=\frac{2}{1+distance}$
            ''', mathjax=True, style={'fontSize': '1.5vw', 'textAlign': 'center'}),
            dcc.Markdown(r'''
            The objective of kappa is to make the prey faster the closer the predator, such that it does not become an easy chase.

            The formula of $\kappa$ is a modified version of the fear function used in **"Predation fear and its carry-over effect in a fractional order prey–predator model with prey refuge"** \[[26](/15)\].

            The plot shows the strength of kappa as a function of distance, with the maximum value being 2 and approaching 0 as the distance increases.
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
        ]
    },

{
    "title": "Experimental Setup",
    "content": [
        html.Div([
            # Left column for text content
            html.Div([
                dcc.Markdown(r'''
                ### Table 1: Simulation Parameters
                - 2D Simulation & Unbounded Environment: The study simulates 2D agents in an unbounded environment, allowing unrestricted movement and realistic behavior analysis.

                - Different $\sigma_c$ for Predators: Predators have different desired distance parameter constants based on their sensing capabilities.
                  Sensing predators can dynamically change their distance based on $\sigma_i$ distance modulation formula, while non-sensing predators have a fixed desired distance constant. A slightly larger $\sigma_c$ to avoid clustering.

                - Larger Dp for DM: In Distance Modulation (DM), the attraction force decreases with distance, requiring a higher sensor range (Dp) to maintain effective peer sensing and prevent swarm separation.

                - Methodology Alignment: Other parameters align with the methodologies detailed in the referenced paper \[[15](/15)\].
                ''', mathjax=True, style={'fontSize': '1.2vw', 'textAlign': 'left'}),
            ], style={'flex': '1', 'padding': '10px', 'width': '30vw'}),  # Adjust width as needed

            # Right column for the LaTeX-rendered table
            html.Div([
                html.Div([
                    dash_katex.DashKatex(id='katex-table',
                        expression=r'''
                        \begin{array}{l|c|l}
                        \hline
                        \text{Parameter} & \text{Value} & \text{Description} \\
                        \hline
                        \text{$\alpha_{predator}$} & 1.0 & \text{Alpha for predators} \\
                        \text{$\alpha_{prey}$} & 1.0 & \text{Alpha for prey} \\
                        \text{$D_{p_{DM}}$} & 4.0 & \text{Sensor range for neighbours (predators) in DM} \\
                        \text{$D_{p_{ADM}}$} & 3.5 & \text{Sensor range for neighbours (predators) in ADM} \\
                        \text{$D_{p_{prey}}$} & 3.5 & \text{Sensor range for neighbours (prey)} \\
                        \text{$\sigma_{c_{SensingPreds}}$} & 0.7 & \text{Constant sigma for DM (sensing predators)} \\
                        \text{$\sigma_{c_{NonSensingPreds}}$} & 0.75 & \text{Constant sigma for DM (non-sensing predators)} \\
                        \text{$\sigma_{c_{predSensingADM}}$} & 1.5 & \text{Constant sigma for ADM (sensing predators)} \\
                        \text{$\sigma_{c_{predNonSensingADM}}$} & 2.0 & \text{Constant sigma for ADM (non-sensing predators)} \\
                        \text{$\sigma_{c_{prey}}$} & 0.7 & \text{Constant sigma for prey} \\
                        \text{error range} & 0.05 & \text{Error range} \\
                        \text{sensor range} & 3 & \text{Sensor range (predator)} \\
                        \text{sensing range} & 3 & \text{Sensing range (prey)} \\
                        \text{$N_{predators}$} & 100 & \text{Number of predators} \\
                        \text{$N_{preys}$} & 100 & \text{Number of prey} \\
                        \text{$dt$} & 0.05 & \text{Time step} \\
                        \text{$\epsilon$} & 12 & \text{Constant multiplier of proximal control vectors} \\
                        \text{$\omega_{max}$} & \frac{\pi}{3} & \text{Maximum angular speed} \\
                        \text{$U_{max}$} & 0.15 & \text{Maximum linear speed} \\
                        \text{$U_{c}$} & 0.05 & \text{Constant linear velocity} \\
                        \hline
                        \end{array}
                        ''',
                        displayMode=False,
                    ),
                ], style={'fontSize': '1.25vw', 'textAlign': 'center'})  # Apply font size and text alignment here
            ], style={'flex': '1', 'padding': '10px', 'width': '45vw'}),  # Adjust width as needed
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'gap': '10px'})  # Add gap to create space between the columns
    ]
}
,
    {
        "title": "Results: Sensing Ranges",
        "content": [

            dcc.Markdown(r'''
            These plots illustrate how different sensing ranges affect the ability of predators to chase preys.

            - These ratios indicate the relative sensing capabilities of predators compared to prey.
              A ratio of 2:1 means that predators can sense prey at twice the distance that prey can sense predators.


            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            dcc.Markdown(r'''
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/sensingRanges_ADM.html", width="100%", height="700px", style={'border': 'none'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
            dcc.Markdown(r'''

            - In both simulations, when all predators are sensing, the plots show that higher predator sensing
                ranges (2:1 and 3:2 ratios) result in a lower average distance between the predator and prey swarms.

            - However, when the sensing ratio is lower (e.g., 1:2), the distance increases, suggesting that predators
              struggles more to keep up with prey when their sensing capability is inferior.

            - The plots have similar trends in all cases, except for the case of only one sensing predator, with DM method.
              In this case, the predator swarm lost the prey 100% of the time.

            - Given that predators, could keep up with prey on a 1:1 ratio, I decided to us this ratio for the rest of the experiments, to make everything fair.

            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/sensingRanges_DM.html", width="100%", height="800px", style={'border': 'none'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
        ]
    },
    {
        "title": "Results: Velocities and Distances (Attractive Distance Modulation)",
        "content": [
            dcc.Markdown(r'''
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/boxplot_ADM.html", width="100%", height="800px", style={'border': 'none'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
            # html.Img(src="assets/boxplot_ADM.html", style={'maxWidth': '100%', 'maxHeight': '500px', 'display': 'block', 'margin': '0 auto'}),
            # html.Br(),  # Adds a vertical space between the iframes
            dcc.Markdown(r'''
            - These figures show the distribution of velocities and distances for the ADM method.

            - In ADM, consistently show lower average distances compared to DM, indicating that predators could either catch or maintain a fixed distance from the prey swarm.

            - The plots show that the hihger the sensory predators, the more likely they are to catch the prey.

            - The velocities of predators are higher than those of preys, as expected. When the predator swarm is fully sensing, the average velocity decreases at step 5000
              indicating that the predator swarm has caught up with the prey swarm, which is further confirmed by the decrease in average distance.
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/speeds_ADM.html", width="100%", height="800px", style={'border': 'none', 'overflow': 'hidden'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
        ]
    },
    {
        "title": "Results: Velocities and Distances (Distance Modulation)",
        "content": [
            dcc.Markdown(r'''

            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/boxplot_DM.html", width="100%", height="800px", style={'border': 'none'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
            dcc.Markdown(r'''
            - Similar to ADM, the higher the sensory predators, the lower the average distance between the predator and prey swarms.

            - Also, similar to ADM, the velocities of predators are higher than those of preys. and maintainng a fixed velocity.

            - Yet, when there are fewer sensing predators, the average distance increases, indicating that the predator swarm struggles to keep up with the prey swarm.
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/speeds_DM.html", width="100%", height="800px", style={'border': 'none'})
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
        ]
    },

    {
        "title": "Discussion",
        "content": [
            html.Div([
                dcc.Markdown(r'''
                - The results show that ADM is more effective than DM in keeping closer distances to preys.

                - Furthermore, the results also show that predators consistently maintain higher velocities than preys.
                ''', mathjax=True, style={'fontSize': '1.5vw'})
            ], style={'flex': '1', 'padding': '10px'}),
            html.Div([
                html.Img(src="assets/PADM_fast.gif", style={'maxWidth': '30vw', 'maxHeight': '50vh', 'display': 'block', 'marginRight': '10px',}),
                html.Img(src="assets/PDM_fast.gif", style={'maxWidth': '30vw', 'maxHeight': '50vh', 'display': 'block', 'marginLeft': '10px', })
            ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'alignItems': 'center', 'overflow': 'hidden'}),
            dcc.Markdown(r'''
            - This is because of the design choice of distance modulation, where we are constantly introducing incentives for predators
              to separate from each other, and run closer towards a prey.

            - Prey on the other hand, do not have this mechanism.

            - Furthermore, these results suggest that this incentive mechanism makes the predatir swarm faster due to the attraction force of the proximal control vector.

            - the two videos show a simulation and the change in velocities of the predators in real time.
              The first video shows the ADM method, and the second video shows the DM method.
              It is clear that in both cases, the predators are consistently faster than the preys. and in the case where both prey and predators have the same proximity control vector,
              although they have similar velocities, the predators are faster.
            ''', mathjax=True, style={'fontSize': '1.5vw'})
        ]

    },
    {
        "title": "Discussion: Velocities and Distances (Distance Modulation)",
        "content": [
            dcc.Markdown(r'''

            - These plots show the average velocities of predators with both methods (ADM and DM) with the presence of preys and without preys, with all sensing predators.
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/comparison_with_preys.html", width="100%", height="700px", style={'border': 'none'}),
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
            dcc.Markdown(r'''
            - In the plot above, the ADM shows a higher velocity than DM and a sudden decrease in velocity at step 5000, indicating that the predator swarm has caught up with the prey swarm.

            - The plot below shows the velocities with no preys, in this case both method show an identical velocity.
            ''', mathjax=True, style={'fontSize': '1.5vw'}),
            html.Div([
            html.Iframe(src="assets/comparison_no_preys.html", width="100%", height="800px", style={'border': 'none'})
            ], style={'flex': '1', 'padding': '10px', 'overflow': 'hidden', 'margin': '0 auto', 'display': 'block', 'justifyContent': 'center'}),
        ]
    },

    {
        "title": "Conclusion",
        "content": [
            dcc.Markdown(r'''

        - ADM vs. DM: Predators using Attractive Distance Modulation (ADM) maintain higher velocities and better prey capture rates compared to Distance Modulation (DM).

        - Building upon previous research: Previous research has used these methods in dynamic gradient maps. Here Preys can be seen as a dynamic gradient in an infinite space.
          proving that this method can be used in more complex scenarios.

        - Future Work: Future research should focus on using ADM for both predator and prey swarms, varying swarm sizes, and testing these algorithms in real-life experiments.
            ''', mathjax=True, style={'fontSize': '1.5vw'})
        ]
    },

{
    "title": "Simulation Playground",
    "content": [
                    dcc.Markdown(r'''
                    *Note*: Since this playground is running with a free hosting service, it will be very slow 😞
                                 
                    The best to play with this slide is to [clone this presentation](https://github.com/Sergi095/Thesis_presentation.git) and run it locally
                                ''', style={'fontSize': '1vw', 'textAlign': 'center'}),

                ],

}
,

    {
        "title": "Acknowledgements",
        "content": [
            dcc.Markdown(r'''
            I would like to express my gratitude to my supervisors, Dr. Eliseo Ferrante and PhD candidate Tugay Alperen Karagüzel, for their invaluable guidance, patience, and support throughout this research project. Their expertise and mentorship have been instrumental in this journey.
                         
            I am also thankful to my wife and friends for their continuous encouragement, understanding, and help during this challenging period.
                         
            Lastly, I would like to extend my appreciation to Vrije Universiteit Amsterdam for providing the resources and environment essential for the successful completion of this project.
            ''', mathjax=True, style={'fontSize': '1.5vw'})
        ]
    },

    {
        "title": "References",
        "content": [
            dcc.Markdown(r'''
            - \[1\] Karaguzel, T.A., Cambier, N., Eiben, A.E., Ferrante, E.: Collective Gradient Following with Sensory Heterogeneous UAV Swarm, pp. 187–201 (2024). https://doi.org/10.1007/978-3-031-51497-5_14
                         
            - \[2\] Wen, T., Gao, Q., Kalm ́ar-Nagy, T., Deng, Y., Cheong, K.H.: A review of predator–prey systems
            with dormancy of predators. Nonlinear dynamics 107(4), 3271–3289 (2022) https://doi.org/10.1007/
            s11071-021-07083-x
                         
            - \[3\] Batabyal, A.: Predator–prey systems as models for integrative research in biology: the value of a non-
            consumptive effects framework. Journal of experimental biology 226(19) (2023) https://doi.org/10.1242/jeb.
            245851
                         
            - \[4\] Diz-Pita, , Otero-Espinar, M.V.: Predator–Prey Models: A Review of Some Recent Advances. Mathematics
            9(15), 1783 (2021) https://doi.org/10.3390/math9151783
                         
            - \[5\] Witkowski, O., Ikegami, T.: Emergence of Swarming Behavior: Foraging Agents Evolve Collective Motion
            Based on Signaling. PloS one 11(4), 0152756 (2016) https://doi.org/10.1371/journal.pone.0152756
                         
            - \[6\] Escobedo, R., Muro, C., Spector, L., Coppinger, R.P.: Group size, individual role differentiation and effec-
            tiveness of cooperation in a homogeneous group of hunters. Journal of the Royal Society interface 11(95),
            20140204 (2014) https://doi.org/10.1098/rsif.2014.0204
                         
            - \[7\] Social Strategies of Carnivorous Mammalian Predators, (2023). https://doi.org/10.1007/978-3-031-29803-5
            . https://doi.org/10.1007/978-3-031-29803-5
                         
            - \[8\] Manubay, J.A., Powell, S.: Detection of prey odours underpins dietary specialization in a Neotropical top-
            predator: How army ants find their ant prey. Journal of animal ecology 89(5), 1165–1174 (2020) https:
            //doi.org/10.1111/1365-2656.13188
                         
            - \[9\] Schnitzler, H.-U., Kalko, E.K.V.: Echolocation by Insect-Eating Bats. BioScience/Bioscience 51(7), 557
            (2001) https://doi.org/10.1641/0006-3568(2001)051
                         
            - \[10\] Olson, R.S., Hintze, A., Dyer, F.C., Knoester, D.B., Adami, C.: Predator confusion is sufficient to evolve
            swarming (2012). https://arxiv.org/abs/1209.3330v1
                         
            
            - \[11\] Chakraborty, D., Bhunia, S., De, R.: Survival chances of a prey swarm: how the cooperative interaction
            range affects the outcome. arXiv (Cornell University) (2019) https://doi.org/10.48550/arxiv.1910.10541
                         
            - \[12\] Papadopoulou, M., Hildenbrandt, H., Sankey, D.W.E., Portugal, S.J., Hemelrijk, C.K.: Self-organization
            of collective escape in pigeon flocks. PLOS computational biology/PLoS computational biology 18(1),
            1009772 (2022) https://doi.org/10.1371/journal.pcbi.1009772
                         
            - \[13\] Marras, S., Domenici, P.: Schooling fish under attack are not all equal: some lead, others follow. PloS one
            8(6), 65784 (2013) https://doi.org/10.1371/journal.pone.0065784
                         
            - \[14\] Duan, H., Huo, M., Fan, Y.: From animal collective behaviors to swarm robotic cooperation. National
            Science Review/National science review 10(5) (2023) https://doi.org/10.1093/nsr/nwad040
                         
            - \[15\] Karag ̈uzel, T.A., Turgut, A.E., Eiben, A.E., Ferrante, E.: Collective gradient perception with a flying robot
            swarm. Swarm intelligence 17(1-2), 117–146 (2022) https://doi.org/10.1007/s11721-022-00220-1
                         
            - \[16\] Wang, G., Xiao, J., Xue, R., Yuan, Y.: A Multi-group Multi-agent System Based on Reinforcement Learning
            and Flocking. International Journal of Control, Automation, and Systems/International journal of control,
            automation, and systems 20(7), 2364–2378 (2022) https://doi.org/10.1007/s12555-021-0170-5
                         
            - \[17\] Lee, K., Ahn, K., Park, J.: End-to-End control of USV swarm using graph centric Multi-Agent Reinforce-
            ment Learning. 2021 21st International Conference on Control, Automation and Systems (ICCAS) (2021)
            https://doi.org/10.23919/iccas52745.2021.9649839
                         
            - \[18\] Hamed, O., Hamlich, M., Ennaji, M.: Hunting strategy for multi-robot based on wolf swarm algorithm and
            artificial potential field. Indonesian journal of electrical engineering and computer science 25(1), 159 (2022)
            https://doi.org/10.11591/ijeecs.v25.i1.pp159-171
                         
            - \[19\] Chen, Y., Kolokolnikov, T.: A minimal model of predator–swarm interactions. Journal of the Royal Society
            interface 11(94), 20131208 (2014) https://doi.org/10.1098/rsif.2013.1208
                         
            - \[20\] Zhdankin, V., Sprott, J.C.: Simple predator-prey swarming model. Physical review. E, Statistical, nonlinear
            and soft matter physics 82(5) (2010) https://doi.org/10.1103/physreve.82.056209
                         
            - \[21\] Li, X., Huang, H., Savkin, A., Zhang, J.: Robotic Herding of Farm Animals Using a Network of Barking
            Aerial Drones. Drones 6(2), 29 (2022) https://doi.org/10.3390/drones6020029
                         
            - \[22\] Xiang, Y., Lei, X., Duan, Z., Dong, F., Gao, Y.: Self-Organized Patchy Target Searching and Collecting
            with Heterogeneous Swarm Robots Based on Density Interactions. Electronics 12(12), 2588 (2023) https:
            //doi.org/10.3390/electronics12122588
                         
            - \[23\] Ordaz-Rivas, E., Torres-Trevi ̃no, L.: Modeling and Simulation of Swarm of Foraging Robots for
            Collecting Resources Using RAOI Behavior Policies, pp. 266–278 (2022). https://doi.org/10.1007/
            978-3-031-19496-2\{ . https://doi.org/10.1007/978-3-031-19496-220
                         
            - \[24\] Ordaz-Rivas, E., Rodriguez-Li ̃nan, A., Torres-Trevi ̃no, L.: Flock of Robots with Self-Cooperation
            for Prey-Predator Task. Journal of intelligent robotic systems 101(2) (2021) https://doi.org/10.1007/
            s10846-020-01283-0
                         
            - \[25\] Sun, X., Hu, C., Liu, T., Yue, S., Peng, J., Fu, Q.: Translating Virtual Prey-Predator Interaction to Real-World
            Robotic Environments: Enabling Multimodal Sensing and Evolutionary Dynamics. Biomimetics 8(8), 580
            (2023) https://doi.org/10.3390/biomimetics8080580
                         
            - \[26\] Balcı, E.: Predation fear and its carry-over effect in a fractional order prey–predator model with prey refuge.
            Chaos, solitons fractals/Chaos, solitons and fractals 175, 114016 (2023) https://doi.org/10.1016/j.chaos.
            2023.114016
                         
            - \[27\] Karag ̈uzel, T.A., Retamal, V., Cambier, N., Ferrante, E.: From Shadows to Light: A Swarm Robotics
            Approach With Onboard Control for Seeking Dynamic Sources in Constrained Environments. IEEE robotics
            automation letters 9(1), 127–134 (2024) https://doi.org/10.1109/lra.2023.3331897
                                    
            ''', mathjax=True, style={'fontSize': '1.2vw', 'maxHeight': '47vh', 'overflow': 'auto', 'scrollbar-width': 'none', '-ms-overflow-style': 'none'}),

        ]
    }
    
]




#############################

simulation = None
predators = None
preys = None
current_step = 0
boundaries = (100, 100)

#############################
app.layout = html.Div([
    html.Div([
        html.Img(src="assets/VU_logo_RGB-01.jpg", style={'maxWidth': '15vw', 'maxHeight': '5vh', 'display': 'block'}),
    ], style={'width': '100%', 'textAlign': 'center', 'margin': '0 auto', 'padding': '1vh 0'}),
    html.H1("Sensory Heterogeneous Predator Swarm vs Fully Sensing Prey Swarm", style={'textAlign': 'center', 'fontSize': '2.5vw', 'margin': '2vh 0'}),
    dcc.Location(id='url', refresh=True),
    html.Div(id='slide-content', style={'width': '80%', 'margin': '0 auto', 'padding': '2vh', 'textAlign': 'left', 'fontSize': '2vw'}),

    html.Div(id='simulation-container'),  # Add this line
    
    html.Div([
        dcc.Input(id='slide-number-input', type='number', min=0, max=len(slides)-1, value=0, 
                  style={'marginRight': '10px', 'padding': '1vh', 'fontSize': '1.2vw', 'width': '60px', 'textAlign': 'center'}),
        html.Span(f"/{len(slides)-1}", style={'fontSize': '1.5vw'}),
    ], style={'textAlign': 'center', 'marginTop': '1vh'}),

    


    html.Div([
        html.Button('Previous', id='prev-button', n_clicks=0, style={'marginRight': '10px', 'padding': '1vh', 'fontSize': '1.2vw', "cursor": "pointer"}),
        html.Button('Next', id='next-button', n_clicks=0, style={'marginLeft': '10px', 'padding': '1vh', 'fontSize': '1.2vw', "cursor": "pointer"}),
    ], style={'textAlign': 'center', 'marginTop': '2vh'}),

    # html.Div(id='simulation-container'),  # Add this line
    
], style={'maxWidth': '100vw', 'margin': '0 auto', 'padding': '2vh 0'})

@app.callback(
    Output('slide-content', 'children'),
    # Output('live-graph', 'figure'),
    Output('url', 'pathname'),
    Output('slide-number-input', 'value'),
    Input('prev-button', 'n_clicks'),
    Input('next-button', 'n_clicks'),
    Input('slide-number-input', 'n_submit'),
    State('slide-number-input', 'value'),
    State('url', 'pathname')
)



def update_slide(prev_clicks, next_clicks, slide_number_submit, slide_number, pathname):
    # Determine the current slide index
    current_index = int(pathname.strip('/')) if pathname and pathname.strip('/').isdigit() else 0

    # Update the slide index based on button clicks or input change
    ctx = dash.callback_context
    if ctx.triggered:
        if 'prev-button' in ctx.triggered[0]['prop_id']:
            current_index = max(0, current_index - 1)
        elif 'next-button' in ctx.triggered[0]['prop_id']:
            current_index = min(len(slides) - 1, current_index + 1)
        elif 'slide-number-input' in ctx.triggered[0]['prop_id']:
            current_index = min(max(0, slide_number), len(slides) - 1)

    # Get the current slide content
    slide = slides[current_index]
    content = html.Div([
        html.Div([
            html.H2(slide['title'], style={'textAlign': 'center', 'padding': '1vh', 'fontSize': '1.5vw'}),
            html.Div(slide['content'], style={'padding': '2vh', 'fontSize': '2vw', 'textAlign': 'left'})
        ], style={'width': '100%'})
    ], style={'width': '100%', 'margin': '0 auto'})

    # Update the URL to reflect the current slide
    return content, f'/{current_index}', current_index


@app.callback(
    Output('simulation-container', 'children'),
    Input('url', 'pathname')
)


def render_simulation(pathname):
    current_index = int(pathname.strip('/')) if pathname and pathname.strip('/').isdigit() else 0
    if current_index == 13:
        return [
            html.Div([
                html.Div([
                    html.Label('Number of Predators', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='n-predators', type='number', value=30, max=50, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    html.Label('Number of Preys', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='n-preys', type='number', value=30, max=50, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    html.Label('Predator Sensor Range', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='predator-sensor-range', type='number', value=3.5, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    html.Label('Prey Sensing Range', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='prey-sensing-range', type='number', value=3.5, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    html.Label('% of Sensing Predators', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='no-sensor', type='number', value=1,min=0, max=1, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    dcc.Checklist(id='pdm', options=[{'label': 'P-ADM', 'value': 'P-ADM'}], value=['P-ADM'], style={'marginBottom': '5px'}),
                    dcc.Checklist(id='pdm-prey', options=[{'label': 'P-ADM Prey', 'value': 'PDM_PREY'}], value=[], style={'marginBottom': '5px'}),
                    html.Label('Steps', style={'display': 'block', 'marginBottom': '5px'}),
                    dcc.Input(id='steps', type='number', value=5000, min=1000, max=10000, step=50, style={'width': '80%', 'padding': '5px', 'marginBottom': '5px'}),
                    html.Div([
                        html.Button('Start', id='start-button', n_clicks=0, style={'padding': '5px 10px', 'marginRight': '5px', 'cursor': 'pointer'}),
                        html.Button('Stop', id='stop-button', n_clicks=0, style={'padding': '5px 10px', 'marginRight': '5px', 'cursor': 'pointer'}),
                        html.Button('Restart', id='restart-button', n_clicks=0, style={'padding': '5px 10px', 'cursor': 'pointer'}),
                    ], style={'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'center', 'marginTop': '10px'}),
                ], style={'width': '30%', 'padding': '10px', 'boxSizing': 'border-box', 'borderRight': '1px solid #ddd', 'marginLeft': '100px'}),
                html.Div([
                    dcc.Graph(id='live-graph', style={'height': '90%', 'width': '80%', 'margin': '0 auto'}),
                    html.Div(id='simulation-status', style={'textAlign': 'left', 'marginTop': '10px', 'fontSize': '1.2vw'}),
                ], style={'width': '70%', 'padding': '10px', 'boxSizing': 'border-box', 'overflow': 'auto', 'scrollbarWidth': 'none'}),
                dcc.Interval(id='interval-component', interval=400, n_intervals=100),
            ], style={'display': 'flex', 'flexDirection': 'row', 'fontSize': '1.vw', 'maxHeight': '47vh', 'overflow': 'auto', 'scrollbarWidth': 'none'})
        ]
    return []




##################################################################################################################################################################################################
@app.callback(
    [Output('live-graph', 'figure'), Output('interval-component', 'disabled'), Output('simulation-status', 'children')],
    [Input('start-button', 'n_clicks'),
     Input('stop-button', 'n_clicks'),
     Input('restart-button', 'n_clicks'),
     Input('interval-component', 'n_intervals')],
    [State('n-predators', 'value'),
     State('n-preys', 'value'),
     State('predator-sensor-range', 'value'),
     State('prey-sensing-range', 'value'),
     State('no-sensor', 'value'),
     State('pdm', 'value'),
     State('pdm-prey', 'value'),
     State('steps', 'value')]
)


def update_simulation(start_clicks, 
                      stop_clicks, 
                      restart_clicks, 
                      n_intervals, 
                      n_predators, 
                      n_preys, 
                      predator_sensor_range, 
                      prey_sensing_range, 
                      no_sensor, 
                      pdm, 
                      pdm_prey, 
                      steps):
    global simulation, predators, preys, current_step

    ctx = dash.callback_context
    if not ctx.triggered:
        return dash.no_update, True, 'Click Start to begin simulation'

    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    # print(button_id)

    if button_id in ['start-button', 'restart-button']:
        current_step = 0
        simulation = PredatorPreySimulation(
            boundaries = boundaries, 
            N = n_predators, 
            N_preys = n_preys, 
            predator_sensor_range = predator_sensor_range,
            sigma_i_pred_non_sensing = 0.75, 
            sigma_i_predator = 0.7,
            sigma_i_pred_non_sensing_DM = 1.4,
            sigma_i_pred_DM = 1.7,
            sigma_i_prey = 0.7,
            epsilon = 12.0,
            epsilon_prey = 12.0, 
            Dp = 4.0, 
            Dp_prey = 3.5, 
            Dp_pm = 3.5,
            Dr = 0.5, 
            L0 = 0.5, 
            k_rep = 2.0, 
            alpha = 1.0, 
            beta = 0.0, 
            gamma = 0.0,
            alpha_prey = 1.0, 
            kappa = 0.0, 
            Uc = 0.05, 
            Umax = 0.15, 
            omegamax = np.pi/3, 
            K1 = 0.5, 
            K2 = 0.05,
            no_sensor = no_sensor,
            pdm = pdm, 
            pdm_prey = pdm_prey,
            prey_sensing_range = prey_sensing_range,
        )

        predators, preys = simulation.generate_agents_and_preys()
        return create_figure(preys, predators), False, 'Simulation started'

    if button_id == 'stop-button':
        # print("Stop button clicked")
        current_step = 0
        simulation = None
        return dash.no_update, False, 'Simulation stopped'

    if button_id == 'interval-component':
        if simulation is not None:
            while current_step < steps:
                preys_, predators_ = simulation.simulate(preys, predators)
                current_step += 1
                # print(current_step)
                if current_step % 50 == 0 or current_step == steps: 
                    return create_figure(preys_, predators_, current_step) , False, 'Simulation running, step: {}'.format(current_step)
                if current_step + 1 == steps:
                    current_step = 0
                    simulation = None
                    # print("Simulation ended")
                    return dash.no_update, False, 'Simulation ended'
    return dash.no_update, False, 'Click Start or Restart to begin simulation'


def create_figure(preys, predators, current_step=0):
    # Calculate the centers of mass for preys and predators
    # print(current_step, "called")    
    prey_center = np.mean(preys[:, :2], axis=0)
    predator_center = np.mean(predators[:, :2], axis=0)
    
    # Calculate the overall center as the midpoint between prey and predator centers
    center_x, center_y = (prey_center + predator_center) / 2
    
    # Calculate the maximum distance from the center to any agent
    all_agents = np.vstack((preys[:, :2], predators[:, :2]))
    max_distance = np.max(np.linalg.norm(all_agents - [center_x, center_y], axis=1))
    
    # Define the plot range (make it slightly larger than max_distance for padding)
    plot_range = max_distance * 2.5

    fig = go.Figure()

    # Function to calculate end points of lines
    def calculate_end_points(agents, line_length=0.5):
        x_start, y_start = agents[:, 0], agents[:, 1]
        x_end = x_start + line_length * np.cos(agents[:, 2])
        y_end = y_start + line_length * np.sin(agents[:, 2])
        return x_start, y_start, x_end, y_end

    # Add preys to the figure
    x_start, y_start, x_end, y_end = calculate_end_points(preys)
    for i in range(len(preys)):
        fig.add_trace(go.Scatter(
            x=[x_start[i], x_end[i]], y=[y_start[i], y_end[i]],
            mode='lines+markers',
            line=dict(color='blue', width=2),
            marker=dict(symbol='arrow', size=8, angleref='previous', color='blue'),
            showlegend=i==0,
            name='Preys'
        ))

    # Add predators to the figure
    predators_with_sensors = predators[predators[:, 3] == 1]
    predators_without_sensors = predators[predators[:, 3] == 0]
    
    # Predators with sensors
    x_start, y_start, x_end, y_end = calculate_end_points(predators_with_sensors)
    for i in range(len(predators_with_sensors)):
        fig.add_trace(go.Scatter(
            x=[x_start[i], x_end[i]], y=[y_start[i], y_end[i]],
            mode='lines+markers',
            line=dict(color='red', width=2),
            marker=dict(symbol='arrow', size=10, angleref='previous', color='red'),
            showlegend=i==0,
            name='Predators with Sensors'
        ))
    
    # Predators without sensors
    x_start, y_start, x_end, y_end = calculate_end_points(predators_without_sensors)
    for i in range(len(predators_without_sensors)):
        fig.add_trace(go.Scatter(
            x=[x_start[i], x_end[i]], y=[y_start[i], y_end[i]],
            mode='lines+markers',
            line=dict(color='green', width=2),
            marker=dict(symbol='arrow', size=10, angleref='previous', color='green'),
            showlegend=i==0,
            name='Predators without Sensors'
        ))

    # Update layout
    fig.update_layout(
        xaxis_range=[center_x - plot_range, center_x + plot_range],
        yaxis_range=[center_y - plot_range, center_y + plot_range],
        xaxis=dict(visible=True, title='X', scaleanchor="y", scaleratio=1),
        yaxis=dict(visible=True, title='Y'),
        showlegend=True,
        margin=dict(l=0, r=0, t=0, b=0),
        width=800,
        height=400
    )
    
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)
    #app.run_server(host='0.0.0.0', port=10000)
