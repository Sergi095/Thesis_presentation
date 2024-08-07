import numpy as np
from typing import Tuple

class PredatorPreySimulation:
    def __init__(self, 
                boundaries = 0.0, 
                N = 10, 
                N_preys = 10, 
                predator_sensor_range = 3,
                sigma_i_pred_non_sensing = 1.0, 
                sigma_i_predator = 1.0,
                sigma_i_pred_non_sensing_DM = 1.0,
                sigma_i_pred_DM = 1.0,
                sigma_i_prey = 1.0,
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
                no_sensor = 0.0,
                pdm = False, 
                pdm_prey = False,
                prey_sensing_range = 3,
                 ):
        self.boundaries = boundaries
        self.N = N
        self.N_preys = N_preys
        self.sensor_range = predator_sensor_range
        self.sigma_i_pred_non_sensing = sigma_i_pred_non_sensing
        self.sigma_i_predator = sigma_i_predator
        self.sigma_i_pred_non_sensing_DM = sigma_i_pred_non_sensing_DM
        self.sigma_i_pred_DM = sigma_i_pred_DM
        self.sigma_i_prey = sigma_i_prey
        self.epsilon = epsilon
        self.epsilon_prey = epsilon_prey
        self.Dp = Dp
        self.Dp_prey = Dp_prey
        self.Dp_pm = Dp_pm
        self.Dr = Dr
        self.L0 = L0
        self.k_rep = k_rep
        self.alpha = alpha
        self.beta = beta
        self.gamma = gamma
        self.alpha_prey = alpha_prey
        self.kappa = kappa
        self.Uc = Uc
        self.Umax = Umax
        self.omegamax = omegamax
        self.K1 = K1
        self.K2 = K2
        self.no_sensor = no_sensor
        self.pdm = pdm
        self.sensing_range = prey_sensing_range

        self.dt = 0.05
        self.error_range = 0.05
        self.pdm_prey = pdm_prey

    def no_sensor_agents(self, no_sensor: float, predators: np.array, preys: np.array) -> np.array:
        N = len(predators)
        no_sensor_agents = np.ones(N)
        no_sensor_count = int(no_sensor * N)
        
        if no_sensor >= 0.10:
            distances = [min(np.linalg.norm(predator[:2] - prey[:2]) for prey in preys) for predator in predators]
            index_distance_pairs = list(enumerate(distances))
            index_distance_pairs.sort(key=lambda x: x[1])
            sorted_indices = [index for index, distance in index_distance_pairs]
            sorted_indices.reverse()
            selected_indices = sorted_indices[:no_sensor_count]
            no_sensor_agents[selected_indices] = 0
            predators[:, 3] = no_sensor_agents
        elif no_sensor != 1:
            selected_indices = np.random.choice(N, size=no_sensor_count, replace=False)
            no_sensor_agents[selected_indices] = 0
            predators[:, 3] = no_sensor_agents

        return predators
    
    def generate_agents_and_preys(self) -> Tuple[np.array, np.array]:
        boundaryX, boundaryY = self.boundaries
        boundaries = (10, 10) if self.boundaries == [0,0] else (boundaryX, boundaryY)
        
        agents = np.ones((self.N, 5))
        preys = np.zeros((self.N_preys, 4))
        
        agents[:, 4] = np.arange(self.N)
        preys[:, 3] = np.arange(self.N_preys)
        
        grid_size_agents = int(np.ceil(np.sqrt(self.N)))
        grid_size_preys = int(np.ceil(np.sqrt(self.N_preys)))
        
        agent_spacing_x = 0.5
        agent_spacing_y = 0.5
        prey_spacing_x = 0.5
        prey_spacing_y = 0.5

        min_distance = (np.sqrt(self.N_preys) * self.sigma_i_prey * prey_spacing_x) + self.sensor_range/1.5 if self.N_preys >= 100 else (np.sqrt(self.N_preys) * self.sigma_i_prey * prey_spacing_x) + self.sensor_range/1.5
        
        agent_idx = 0
        for i in range(grid_size_agents):
            for j in range(grid_size_agents):
                if agent_idx < self.N:
                    x = i * agent_spacing_x + agent_spacing_x / 2
                    y = j * agent_spacing_y + agent_spacing_y / 2
                    theta = np.random.uniform(0, 2*np.pi)
                    agents[agent_idx, :3] = np.array([x, y, theta])
                    agent_idx += 1
        
        prey_idx = 0
        signx = np.random.choice([-1, 1])
        signy = np.random.choice([-1, 1])
        for i in range(grid_size_preys):
            for j in range(grid_size_preys):
                if prey_idx < self.N_preys:
                    x = i * prey_spacing_x + prey_spacing_x / 2 + signx* min_distance
                    y = j * prey_spacing_y + prey_spacing_y / 2 + signy* min_distance
                    theta = np.random.uniform(0, 2*np.pi)
                    preys[prey_idx, :3] = np.array([x, y, theta])
                    prey_idx += 1
        
        agents = self.no_sensor_agents(self.no_sensor, agents, preys)
        
        return agents, preys

    def get_distance_matrix(self, agents: np.array) -> np.array:
        positions_x = agents[:, 0]
        positions_y = agents[:, 1]
        N = len(positions_x)
        
        distance_matrix = np.linalg.norm(agents[:, np.newaxis, :2] - agents[np.newaxis, :, :2], axis=-1) # N x N matrix
        np.fill_diagonal(distance_matrix, np.inf) 

        return distance_matrix
    
    def get_distance_from_swarm_preys(self, preys: np.array, predators: np.array) -> np.array:
        # Calculate distances between each predator and each prey
        prey_positions = preys[:, :2]  # Extract prey positions
        predator_positions = predators[:, :2]  # Extract predator positions

        # Calculate distances between each predator and each prey using broadcasting
        distances = np.linalg.norm(predator_positions[:, None, :] - prey_positions[None, :, :], axis=2)

        # Create a mask for prey within the sensor range of each predator
        mask = distances <= self.sensor_range

        result = np.zeros(predators.shape[0])

        for i in range(predators.shape[0]):
            # Get distances of prey within sensor range of the current predator
            within_range_distances = distances[i][mask[i]]

            if within_range_distances.size > 0:
                # Average the distances within the sensor range
                avg_distance = np.mean(within_range_distances)
                
                # Compute the result as 1/distance
                result[i] = 1 / avg_distance

        return result


    def get_angle_matrix(self, agents: np.array) -> np.array:
        positions_x = agents[:, 0]
        positions_y = agents[:, 1]
        N = len(positions_x)
        
        angles = np.arctan2(positions_y[:, np.newaxis] - positions_y[np.newaxis, :], positions_x[:, np.newaxis] - positions_x[np.newaxis, :]) # N x N matrix
        np.fill_diagonal(angles, np.inf) 

        return angles


    def p_vector_prey(self, preys):
        N = len(preys)

        self.sigma_i = 1.0
        self.sigma_i = np.tile(self.sigma_i, (N,N))
        self.sigma_i *= self.sigma_i_prey

        dist_matrix = self.get_distance_matrix(preys)
        phi = self.get_angle_matrix(preys)
        mask = dist_matrix <= self.Dp_prey

        distance = dist_matrix[mask]
        # distance += 1e-10
        phi_im = phi[mask]
        sigma_i_masked = self.sigma_i[mask]

        if self.pdm_prey:
            px = -((self.epsilon_prey / 1.0) * ((sigma_i_masked / distance) - np.sqrt(sigma_i_masked / distance))) * np.cos(phi_im)
            py = -((self.epsilon_prey / 1.0) * ((sigma_i_masked / distance) - np.sqrt(sigma_i_masked / distance))) * np.sin(phi_im)
        else:
            px = -self.epsilon_prey * ((2.0 * sigma_i_masked**4) / (distance**5) - (sigma_i_masked**2) / (distance**3)) * np.cos(phi_im)
            py = -self.epsilon_prey * ((2.0 * sigma_i_masked**4) / (distance**5) - (sigma_i_masked**2) / (distance**3)) * np.sin(phi_im)

        p_vectors = np.zeros((N, N, 2))
        p_values = np.stack((px, py), axis=-1)
        p_vectors[mask] = p_values

        return np.sum(p_vectors, axis=0)


    def p_vector(self, agents, distance_swarm_prey):
        N = len(agents)


        self.sigma_i = 1.0
        self.sigma_i = np.tile(self.sigma_i, (N,N))
        no_distance_sensor_agents = agents[:, 3] == 0
        self.sigma_i[no_distance_sensor_agents] *= self.sigma_i_pred_non_sensing
        self.sigma_i[~no_distance_sensor_agents] *= self.sigma_i_predator
        
        # Reshape distance_swarm_prey to match self.sigma_i
        # distance_swarm_prey = distance_swarm_prey.reshape(-1, 1)
        # distance_swarm_prey = np.tile(distance_swarm_prey, (1, N))
        
        # Replace distance with 0 if agent is not a distance sensor
        distance_swarm_prey = np.where(agents[:, 3][:, np.newaxis] == 0, 0, distance_swarm_prey)
        
        # Add the distance effect to the diagonal of self.sigma_i
        # np.fill_diagonal(self.sigma_i, np.diag(self.sigma_i) + distance_swarm_prey.diagonal())
        self.sigma_i += 3*(distance_swarm_prey) * np.diag(self.sigma_i) #+ 1.e-6

        dist_matrix = self.get_distance_matrix(agents)
        phi = self.get_angle_matrix(agents)
        mask = dist_matrix <= (self.Dp_pm if self.pdm else self.Dp)

        distance = dist_matrix[mask]
        # distance += 1e-10
        phi_im = phi[mask]
        sigma_i_masked = self.sigma_i[mask]

        if self.pdm:
            px = -((self.epsilon / 1.0) * ((sigma_i_masked / distance) - np.sqrt(sigma_i_masked / distance))) * np.cos(phi_im)
            py = -((self.epsilon / 1.0) * ((sigma_i_masked / distance) - np.sqrt(sigma_i_masked / distance))) * np.sin(phi_im)
        else:
            px = -self.epsilon * ((2.0 * sigma_i_masked**4) / (distance**5) - (sigma_i_masked**2) / (distance**3)) * np.cos(phi_im)
            py = -self.epsilon * ((2.0 * sigma_i_masked**4) / (distance**5) - (sigma_i_masked**2) / (distance**3)) * np.sin(phi_im)

        p_vectors = np.zeros((N, N, 2))
        p_values = np.stack((px, py), axis=-1)
        p_vectors[mask] = p_values

        # print(np.sum(p_vectors, axis=0))
        return np.sum(p_vectors, axis=0)  # N x 2

    def repulsion_predator(self, preys: np.array, predators: np.array) -> np.array:
        positions_preys = preys[:, :2]
        positions_predators = predators[:, :2]
        sensing_range = self.sensing_range
        N = len(preys)
        M = len(predators)

        # Calculate the distance matrix (N x M)
        distance_matrix = np.linalg.norm(positions_preys[:, np.newaxis] - positions_predators[np.newaxis], axis=-1)
        
        # Create a mask for predators within the sensing range of each prey
        mask = distance_matrix <= sensing_range

        # Initialize the repulsion vector
        repulsion_vector = np.zeros((N, 2))

        for i in range(N):
            # Get indices of predators within sensing range of the current prey
            within_range_indices = np.where(mask[i])[0]
            
            if within_range_indices.size > 0:
                average_preds = np.mean(positions_predators[within_range_indices], axis=0)

                # Calculate the direction vector from prey to average position of nearby predators
                direction_x = positions_preys[i, 0] - average_preds[0]
                direction_y = positions_preys[i, 1] - average_preds[1]
                distances = np.linalg.norm([direction_x, direction_y])
                kappa = 2.0 / (1+distances)
                repulsion_vector[i, 0] = kappa * direction_x
                repulsion_vector[i, 1] = kappa * direction_y
        return repulsion_vector


    def update_agents(self, agents, vectors, is_prey=False):

        if is_prey == False:
            # print(agents)
            # print(len(agents))
            force = self.alpha * vectors['p']

            # project from global to local reference frame
            fx = np.sqrt(force[:, 0, np.newaxis]**2 + force[:, 1, np.newaxis]**2) * np.cos(np.arctan2(force[:, 1,np.newaxis], force[:, 0,np.newaxis]) - agents[:, 2, np.newaxis])
            fy = np.sqrt(force[:, 0, np.newaxis]**2 + force[:, 1, np.newaxis]**2) * np.sin(np.arctan2(force[:, 1,np.newaxis], force[:, 0,np.newaxis]) - agents[:, 2, np.newaxis])

            fx = np.squeeze(fx)
            fy = np.squeeze(fy)

            # Compute the U_i and omega_i for the agents
            U_i = self.K1 * fx + self.Uc
            omega_i = self.K2 * fy

            # RULES FROM PAPER
            U_i = np.where(U_i < 0, 0, U_i)
            U_i = np.where(U_i > self.Umax, self.Umax, U_i)

            omega_i = np.where(omega_i < -self.omegamax, -self.omegamax, omega_i)
            omega_i = np.where(omega_i > self.omegamax, self.omegamax, omega_i)

            # Update the states of the agents
            error_x = np.random.uniform(-self.error_range, self.error_range, self.N) * self.dt
            error_y = np.random.uniform(-self.error_range, self.error_range, self.N) * self.dt

            dx = U_i * np.cos(agents[:, 2]) * self.dt + error_x
            dy = U_i * np.sin(agents[:, 2]) * self.dt + error_y

            agents[:, 0] = agents[:, 0] + dx
            agents[:, 1] = agents[:, 1] + dy

            agents[:, 2] = agents[:, 2] + omega_i * self.dt

            return agents
        else:
            # print('prey')
            # print(len(agents))
            force = self.alpha_prey * vectors['p'] + vectors['r']

            # project from global to local reference frame
            fx = np.sqrt(force[:, 0, np.newaxis]**2 + force[:, 1, np.newaxis]**2) * np.cos(np.arctan2(force[:, 1,np.newaxis], force[:, 0,np.newaxis]) - agents[:, 2, np.newaxis])
            fy = np.sqrt(force[:, 0, np.newaxis]**2 + force[:, 1, np.newaxis]**2) * np.sin(np.arctan2(force[:, 1,np.newaxis], force[:, 0,np.newaxis]) - agents[:, 2, np.newaxis])

            fx = np.squeeze(fx)
            fy = np.squeeze(fy)

            # Compute the U_i and omega_i for the agents
            U_i = self.K1 * fx + self.Uc
            omega_i = self.K2 * fy

            # RULES FROM PAPER
            U_i = np.where(U_i < 0, 0, U_i)
            U_i = np.where(U_i > self.Umax, self.Umax, U_i)

            omega_i = np.where(omega_i < -self.omegamax, -self.omegamax, omega_i)
            omega_i = np.where(omega_i > self.omegamax, self.omegamax, omega_i)

            # Update the states of the agents
            error_x = np.random.uniform(-self.error_range, self.error_range, self.N_preys) * self.dt
            error_y = np.random.uniform(-self.error_range, self.error_range, self.N_preys) * self.dt

            dx = U_i * np.cos(agents[:, 2]) * self.dt + error_x
            dy = U_i * np.sin(agents[:, 2]) * self.dt + error_y

            agents[:, 0] = agents[:, 0] + dx
            agents[:, 1] = agents[:, 1] + dy

            agents[:, 2] = agents[:, 2] + omega_i * self.dt

            return agents



    def simulate(self, preys, predators):
        distance_swarm_prey = self.get_distance_from_swarm_preys(preys, predators)

        prey_vectors = {
            'r': self.repulsion_predator(preys, predators),
            'p': self.p_vector_prey(preys)
        }
        predator_vectors = {
            'p': self.p_vector(predators, distance_swarm_prey)
        }

        
        updated_predators = self.update_agents(predators, predator_vectors, is_prey=False)
        updated_preys     = self.update_agents(preys, prey_vectors, is_prey=True)
        return updated_preys, updated_predators
