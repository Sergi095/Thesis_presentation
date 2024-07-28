import dash
from dash import dcc, html, Input, Output, State
import dash_katex
# Initialize the Dash app
app = dash.Dash(__name__, title='Thesis Presentation')

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
                - Introduction
                - Related Work
                - Methods
                - Experimental Setup
                - Results
                - Discussion
                - Conclusions
                ''', mathjax=True, style={'fontSize': '1.2vw'}),
            ], style={'flex': '1', 'padding': '10px'}),
            html.Div([
                html.Img(src="assets/2Dfast.gif", style={'maxWidth': '25vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginRight': '10px'}),
                html.Img(src="assets/pybulletFast.gif", style={'maxWidth': '25vw', 'maxHeight': '40vh', 'display': 'block', 'margin': '0 auto', 'marginLeft': '10px'})
            ], style={'flex': '1', 'padding': '10px', 'display': 'flex', 'flexDirection': 'row', 'justifyContent': 'flex-start', 'alignItems': 'flex-end'})
        ], style={'display': 'flex', 'flexDirection': 'row'}),
        html.Div([
            dcc.Markdown(r'''
            ### Project Code
            ''', mathjax=True, style={'fontSize': '1.2vw', 'alignItems':'center'}),
            html.A([
                html.Img(src="assets/GitHub_logo.png", style={'maxWidth': '20px', 'maxHeight': '20px', 'marginRight': '5px'}),
                "Github Repository"
            ], href="https://github.com/Sergi095/Vu_Thesis_Prey_Predator.git", style={'textDecoration': 'none', 'fontSize': '1.2vw', 'alignItems': 'center'})
        ], style={'flex': '1', 'padding': '10px', 'alignItems': 'center'}),
    ]
},
    {
        "title": "Introduction",
        "content": [
            html.Div([
                dcc.Markdown(r'''

                - The dynamics between prey and predators have been extensively studied across fields like mathematics, robotics, and biology.
                  These studies help us understand population dynamics, migrations, and species adaptation.
                  In multi-agent environments, both predators and prey may evolve swarming behaviors for escape or chase strategies. \[[2-5](/14)\]

                - Predators often hunt collectively to capture challenging prey, despite the cost of sharing.
                  Examples include lions, hyenas, wolves, and killer whales.
                  Their hunting strategies vary significantly, utilizing senses like sight, smell, and echolocation. \[[6-9](/14)\]

                - Prey develop swarming behaviors to increase survival chances, such as confusing predators.
                 Examples include pigeons and fish, which exhibit complex escape patterns through self-organization and group behaviors. \[[10-13](/14)\]

                - Inspired by these natural behaviors, researchers have developed swarm robotic systems to mimic these interactions for complex tasks.
                  This study explores mechanisms like Distance Modulation (DM) and Attractive Distance Modulation (ADM) in a dynamic environment. \[[15](/14)\]
                ''', mathjax=True, style={'fontSize': '1.5vw'})
            ], style={'flex': '1', 'padding': '10px'})
        ]
    },
    {
        "title": "Related Work",
        "content": [
            html.Div([
                dcc.Markdown(r'''

                - Reinforcement Learning Approaches: Studies integrating Reinforcement Learning (RL) with flocking control to model predator-prey interactions, showing improved learning efficiency and coordination. \[[16-18](/14)\]

                - Mathematical Models and Theoretical Analysis: Development of minimal models and particle-based approaches to study predator-swarm dynamics, revealing various interaction patterns like escape, confusion, and capture. \[[19-20](/14)\]

                - Applications and Practical Implementations: Use of prey-predator algorithms in real-world scenarios such as surveillance and herding with autonomous drones, demonstrating the practical utility of swarm robotics. \[[21-22](/14)\]

                - Swarm Robotics and Flocking Behavior: Research on RAOI behavior policies and prey-predator tasks to enhance cooperative behavior and efficiency in robotic swarms. \[[23-25](/14)\]
                ''', mathjax=True, style={'fontSize': '1.5vw'})
            ], style={'flex': '1', 'padding': '10px'})
        ]
    },

    {
        "title": "Methods: Proximal Control Vectors",
        "content": [
            dcc.Markdown(r'''
            Following the methodology of “Collective Gradient Following with Sensory Heterogeneous UAV Swarm” \[[1](/14)\] I implement two different proximal control vectors:
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

            The formula of $\kappa$ is a modified version of the fear function used in **"Predation fear and its carry-over effect in a fractional order prey–predator model with prey refuge"** \[[26](/14)\].

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

                - Methodology Alignment: Other parameters align with the methodologies detailed in the referenced paper \[[15](/14)\].
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

            - \[1\] T. A. Karagüzel, N. Cambier, A. E. Eiben, and E. Ferrante, “Collective Gradient Following with Sensory Heterogeneous UAV Swarm,” in Springer proceedings in advanced robotics, 2024, pp. 187–201. doi: 10.1007/978-3-031-51497-5_14.
                         
            - \[2\] T. Wen, Q. Gao, T. Kalmár-Nagy, Y. Deng, and K. H. Cheong, “A review of predator–prey systems with dormancy of predators,” Nonlinear Dynamics, vol. 107, no. 4, pp. 3271–3289, Jan. 2022, doi: 10.1007/s11071-021-07083-x.
                         
            - \[3\] A. Batabyal, “Predator–prey systems as models for integrative research in biology: the value of a non-consumptive effects framework,” Journal of Experimental Biology, vol. 226, no. 19, Sep. 2023, doi: 10.1242/jeb.245851.
                         
            - \[4\] É. Diz-Pita and M. V. Otero-Espinar, “Predator–Prey Models: A review of some recent advances,” Mathematics, vol. 9, no. 15, p. 1783, Jul. 2021, doi: 10.3390/math9151783.
                         
            - \[5\] O. Witkowski and T. Ikegami, “Emergence of swarming behavior: Foraging agents evolve collective motion based on signaling,” PLoS ONE, vol. 11, no. 4, p. e0152756, Apr. 2016, doi: 10.1371/journal.pone.0152756.
                         
            - \[6\] R. Escobedo, C. Muro, L. Spector, and R. P. Coppinger, “Group size, individual role differentiation and effectiveness of cooperation in a homogeneous group of hunters,” Journal of the Royal Society Interface, vol. 11, no. 95, p. 20140204, Jun. 2014, doi: 10.1098/rsif.2014.0204.
                         
            - \[7\] M. Srinivasan and B. Würsig, Social strategies of carnivorous mammalian predators. 2023. doi: 10.1007/978-3-031-29803-5.
                         
            - \[8\] J. A. Manubay and S. Powell, “Detection of prey odours underpins dietary specialization in a Neotropical top‐predator: How army ants find their ant prey,” Journal of Animal Ecology, vol. 89, no. 5, pp. 1165–1174, Mar. 2020, doi: 10.1111/1365-2656.13188.
                         
            - \[9\] H.-U. Schnitzler and E. K. V. Kalko, “Echolocation by Insect-Eating bats,” BioScience, vol. 51, no. 7, p. 557, Jan. 2001, doi: 10.1641/0006-3568(2001)051.
                         
            - \[10\] R. S. Olson, A. Hintze, F. C. Dyer, D. B. Knoester, and C. Adami, “Predator confusion is sufficient to evolve swarming,” arXiv.org, Sep. 14, 2012. https://arxiv.org/abs/1209.3330v1
                         
            - \[11\] D. Chakraborty, S. Bhunia, and R. De, “Survival chances of a prey swarm: how the cooperative interaction range affects the outcome,” arXiv.org, Oct. 23, 2019. https://arxiv.org/abs/1910.10541
                         
            - \[12\] M. Papadopoulou, H. Hildenbrandt, D. W. E. Sankey, S. J. Portugal, and C. K. Hemelrijk, “Self-organization of collective escape in pigeon flocks,” PLOS Computational Biology/PLoS Computational Biology, vol. 18, no. 1, p. e1009772, Jan. 2022, doi: 10.1371/journal.pcbi.1009772.
                         
            - \[13\] S. Marras and P. Domenici, “Schooling fish under attack are not all equal: some lead, others follow,” PloS One, vol. 8, no. 6, p. e65784, Jun. 2013, doi: 10.1371/journal.pone.0065784.
                         
            - \[14\] H. Duan, M. Huo, and Y. Fan, “From animal collective behaviors to swarm robotic cooperation,” National Science Review/National Science Review, vol. 10, no. 5, Feb. 2023, doi: 10.1093/nsr/nwad040.
                         
            - \[15\] T. A. Karagüzel, A. E. Turgut, A. E. Eiben, and E. Ferrante, “Collective gradient perception with a flying robot swarm,” Swarm Intelligence, vol. 17, no. 1–2, pp. 117–146, Oct. 2022, doi: 10.1007/s11721-022-00220-1.
                         
            - \[16\] G. Wang, J. Xiao, R. Xue, and Y. Yuan, “A multi-group multi-agent system based on reinforcement learning and flocking,” International Journal of Control, Automation, and Systems/International Journal of Control, Automation, and Systems, vol. 20, no. 7, pp. 2364–2378, Jun. 2022, doi: 10.1007/s12555-021-0170-5.
                         
            - \[17\] “End-to-End control of USV swarm using graph centric Multi-Agent Reinforcement Learning,” IEEE Conference Publication | IEEE Xplore, Oct. 12, 2021. https://ieeexplore.ieee.org/document/9649839/
                         
            - \[18\] O. Hamed, M. Hamlich, and M. Ennaji, “Hunting strategy for multi-robot based on wolf swarm algorithm and artificial potential field,” Indonesian Journal of Electrical Engineering and Computer Science, vol. 25, no. 1, p. 159, Jan. 2022, doi: 10.11591/ijeecs.v25.i1.pp159-171.
                         
            - \[19\] Y. Chen and T. Kolokolnikov, “A minimal model of predator–swarm interactions,” Journal of the Royal Society Interface, vol. 11, no. 94, p. 20131208, May 2014, doi: 10.1098/rsif.2013.1208.
                         
            - \[20\] V. Zhdankin and J. C. Sprott, “Simple predator-prey swarming model,” Physical Review E, vol. 82, no. 5, Nov. 2010, doi: 10.1103/physreve.82.056209.
                         
            - \[21\] X. Li, H. Huang, A. Savkin, and J. Zhang, “Robotic herding of farm animals using a network of barking aerial drones,” Drones, vol. 6, no. 2, p. 29, Jan. 2022, doi: 10.3390/drones6020029.
                         
            - \[22\] Y. Xiang, X. Lei, Z. Duan, F. Dong, and Y. Gao, “Self-Organized Patchy Target Searching and Collecting with Heterogeneous Swarm Robots Based on Density Interactions,” Electronics, vol. 12, no. 12, p. 2588, Jun. 2023, doi: 10.3390/electronics12122588.
                         
            - \[23\] E. Ordaz-Rivas and L. Torres-Treviño, “Modeling and simulation of swarm of foraging robots for collecting resources using RAOI behavior Policies,” in Lecture notes in computer science, 2022, pp. 266–278. doi: 10.1007/978-3-031-19496-2_20.
                         
            - \[24\] E. Ordaz-Rivas, A. Rodriguez-Liñan, and L. Torres-Treviño, “Flock of Robots with Self-Cooperation for Prey-Predator Task,” Journal of Intelligent & Robotic Systems, vol. 101, no. 2, Feb. 2021, doi: 10.1007/s10846-020-01283-0.
                        
            - \[25\] X. Sun, C. Hu, T. Liu, S. Yue, J. Peng, and Q. Fu, “Translating virtual Prey-Predator interaction to Real-World robotic environments: enabling multimodal sensing and evolutionary dynamics,” Biomimetics, vol. 8, no. 8, p. 580, Dec. 2023, doi: 10.3390/biomimetics8080580.
                         
            - \[26\] E. Balcı, “Predation fear and its carry-over effect in a fractional order prey–predator model with prey refuge,” Chaos, Solitons & Fractals/Chaos, Solitons and Fractals, vol. 175, p. 114016, Oct. 2023, doi: 10.1016/j.chaos.2023.114016.
                         
            ''', mathjax=True, style={'fontSize': '1.2vw', 'maxHeight': '47vh', 'overflow': 'auto', 'scrollbar-width': 'none', '-ms-overflow-style': 'none'}),

        ]
    }

]


app.layout = html.Div([
    html.Div([
        html.Img(src="assets/VU_logo_RGB-01.jpg", style={'maxWidth': '15vw', 'maxHeight': '5vh', 'display': 'block'}),
    ], style={'width': '100%', 'textAlign': 'center', 'margin': '0 auto', 'padding': '1vh 0'}),
    html.H1("Sensory Heterogeneous Predator Swarm vs Fully Sensing Prey Swarm", style={'textAlign': 'center', 'fontSize': '2.5vw', 'margin': '2vh 0'}),
    dcc.Location(id='url', refresh=False),
    html.Div(id='slide-content', style={'width': '80%', 'margin': '0 auto', 'padding': '2vh', 'textAlign': 'left', 'fontSize': '2vw'}),
    html.Div([
        dcc.Input(id='slide-number-input', type='number', min=0, max=len(slides)-1, value=0,
                  style={'marginRight': '10px', 'padding': '1vh', 'fontSize': '1.2vw', 'width': '60px', 'textAlign': 'center', 'scrollbar-width': 'none', '-ms-overflow-style': 'none'}),
        html.Span(f"/{len(slides)-1}", style={'fontSize': '1.5vw'}),
    ], style={'textAlign': 'center', 'marginTop': '1vh'}),
    html.Div([
        html.Button('Previous', id='prev-button', n_clicks=0, style={'marginRight': '10px', 'padding': '1vh', 'fontSize': '1.2vw', "pointer": "cursor"}),
        html.Button('Next', id='next-button', n_clicks=0, style={'marginLeft': '10px', 'padding': '1vh', 'fontSize': '1.2vw', "pointer": "cursor"}),
    ], style={'textAlign': 'center', 'marginTop': '2vh', "pointer": "cursor"}),
], style={'maxWidth': '100vw', 'margin': '0 auto', 'padding': '2vh 0', 'scrollbar-width': 'none', '-ms-overflow-style': 'none'})

@app.callback(
    Output('slide-content', 'children'),
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

if __name__ == '__main__':
    app.run_server(debug=True)