// This file defines your entire CI/CD pipeline
pipeline {
    // 1. Agent: Run on any available Jenkins agent
    agent any

    // 2. Stages: The steps of our pipeline
    stages {
        
        // --- NEW STAGE: INSTALL DOCKER & KUBECTL ---
        // We run this as root (which we set in the docker run command)
        // to install the CLIs we need.
        stage('0. Install Tools') {
            steps {
                // --- FIX 1: 'user' command now wraps the 'sh' command ---
                user('root') {
                    sh 'apt-get update && apt-get install -y docker.io kubectl'
                }
            }
        }

        // --- STAGE 1: CHECKOUT ---
        stage('1. Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/NehaMtechBits/Devops-Assingment'
            }
        }

        // --- STAGE 2: RUN UNIT TESTS ---
        // This stage now runs inside its own temporary Docker container
        stage('2. Run Unit Tests') {
            agent {
                // Use an official Python 3.9 image
                docker { image 'python:3.9-slim' }
            }
            steps {
                sh 'echo "--- Installing dependencies ---"'
                sh 'pip install -r requirements.txt'
                
                sh 'echo "--- Running Pytest ---"'
                sh 'pytest'
            }
        }

        // --- STAGE 3: SONARQUBE ANALYSIS ---
        stage('3. SonarQube Analysis') {
            steps {
                script {
                    def sonar = tool 'SonarScanner' 
                    withSonarQubeEnv('SonarQubeServer') {
                        sh "${sonar}/bin/sonar-scanner"
                    }
                }
            }
        }

        // --- STAGE 4: BUILD DOCKER IMAGE ---
        stage('4. Build Docker Image') {
            steps {
                sh 'echo "--- Building Docker Image ---"'
                // !! REPLACE 'nehamtechbits' with your Docker Hub username !!
                sh 'docker build -t nehamtechbits/aceest-fitness:${GIT_COMMIT} -t nehamtechbits/aceest-fitness:latest .'
            }
        }

        // --- STAGE 5: PUSH TO DOCKER HUB ---
        stage('5. Push to Docker Hub') {
            steps {
                // --- FIX 2: Variable names now match the sh script ---
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'nehapandya', passwordVariable: 'Mamra#7041')]) {
                    sh 'echo "--- Logging into Docker Hub ---"'
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    
                    sh 'echo "--- Pushing Image ---"'
                    // !! REPLACE 'nehamtechbits' with your Docker Hub username !!
                    sh 'docker push nehamtechbits/aceest-fitness:latest'
                    sh 'docker push nehamtechbits/aceest-fitness:${GIT_COMMIT}'
                }
            }
        }

        // --- STAGE 6: DEPLOY TO KUBERNETES ---
        stage('6. Deploy to Kubernetes') {
            steps {
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh 'echo "--- Applying Kubernetes manifests ---"'
                    sh 'kubectl apply -f k8s/'
                    
                    sh 'echo "--- Waiting for deployment to complete ---"'
                    sh 'kubectl rollout status deployment/aceest-deployment'
                    
                    sh 'echo "--- Deployment Successful! ---"'
                }
            }
        }
    }
}
```

### What To Do Now

1.  **Replace** the code in your `Jenkinsfile` with the corrected code above.
2.  **Commit and push** this fix:
    ```bash
    git add Jenkinsfile
    git commit -m "Fix: Correct user() syntax and docker credentials in Jenkinsfile"
    git push origin main