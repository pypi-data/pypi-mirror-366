 def spectral_bias(self):
        """
        Computes the spectral bias of the DMD model in order to optimize hyperparameter (rank)
        #TODO: this could be very wrong, check it!
        """
        #iteratively recomputes self.A_v for different ranks, and extracts eigenvalues
        #identifies the metric distortion as : sqrt(v_i^* U_r^T K_xy U_r v_i / ||K_xy U_r v_i||)
        self.metric_distortions = np.zeros((self.rank))
        self.spectral_biases = np.zeros((self.rank))
        for rank in range(1,self.rank):
            A_tmp = self.V_kernel[:,:rank].T @ self.k_yx @ self.U_kernel[:,:rank]
            _, evecs = np.linalg.eig(A_tmp)
            #i think evecs[:,i].T should be evecs[:,i].conj().T
            self.metric_distortions[rank] = np.sqrt(evecs[:,-1].T @ self.U_kernel[:,:rank].T @ self.k_yx @ self.U_kernel[:,:rank] @ evecs[:,-1] 
                                                     / np.linalg.norm(self.k_yx @ self.U_kernel[:,:rank] @ evecs[:,-1]))
            print(self.metric_distortions[rank] * self.sigma_sq[rank])    
            self.spectral_biases[rank] = self.metric_distortions[rank] * self.sigma_