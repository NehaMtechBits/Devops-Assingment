// This file defines your entire CI/CD pipeline
pipeline {
    // 1. Agent: Run on any available Jenkins agent
    agent any

    // 2. Stages: The steps of our pipeline
    stages {

        // --- STAGE 1: CHECKOUT ---
        // Clones your Git repository
        stage('1. Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/NehaMtechBits/Devops-Assingment'
            }
        }

        // --- STAGE 2: RUN UNIT TESTS ---
        // Runs the Pytest-based tests. If this fails, the pipeline stops.
        stage('2. Run Unit Tests') {
            steps {
                sh 'echo "--- Installing dependencies ---"'
                // We use python -m to avoid PATH issues
                sh 'python -m pip install -r requirements.txt'
                
                sh 'echo "--- Running Pytest ---"'
                sh 'python -m pytest'
            }
        }

        // --- STAGE 3: SONARQUBE ANALYSIS ---
        // Runs static code analysis. Assumes you have SonarQube setup.
        stage('3. SonarQube Analysis') {
            steps {
                script {
                    // 'SonarScanner' is the name from Jenkins Global Tool Config
                    // 'SonarQubeServer' is the name from Jenkins Configure System
                    // This step requires the sonar-project.properties file
                    def sonar = tool 'SonarScanner' 
                    withSonarQubeEnv('SonarQubeServer') {
                        sh "${sonar}/bin/sonar-scanner"
                    }
                }
            }
        }

        // --- STAGE 4: BUILD DOCKER IMAGE ---
        // Builds the image using your Dockerfile
        stage('4. Build Docker Image') {
            steps {
                sh 'echo "--- Building Docker Image ---"'
                // We tag the image with the unique Git commit hash and 'latest'
                // !! REPLACE 'your-dockerhub-username' with your actual username !!
                sh 'docker build -t nehapandya/aceest-fitness:${GIT_COMMIT} -t nehapandya/aceest-fitness:latest .'
            }
        }

        // --- STAGE 5: PUSH TO DOCKER HUB ---
        // Logs into Docker Hub and pushes the image
        stage('5. Push to Docker Hub') {
            steps {
                // 'dockerhub-creds' is the ID you set up in Jenkins Credentials
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'nehapandya', passwordVariable: 'Mamra#7041')]) {
                    sh 'echo "--- Logging into Docker Hub ---"'
                    sh 'echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin'
                    
                    sh 'echo "--- Pushing Image ---"'
                    // !! REPLACE 'your-dockerhub-username' with your actual username !!
                    sh 'docker push your-dockerhub-username/aceest-fitness:latest'
                    sh 'docker push your-dockerhub-username/aceest-fitness:${GIT_COMMIT}'
                }
            }
        }

        // --- STAGE 6: DEPLOY TO KUBERNETES ---
        // Applies the Kubernetes .yaml files to deploy the app
        stage('6. Deploy to Kubernetes') {
            steps {
                // 'kubeconfig' is the ID for your Kubernetes config credential
                withKubeConfig([credentialsId: 'kubeconfig']) {
                    sh 'echo "--- Applying Kubernetes manifests ---"'
                    // This command applies all .yaml files in the k8s/ directory
                    sh 'kubectl apply -f k8s/'
                    
                    sh 'echo "--- Waiting for deployment to complete ---"'
                    // This waits for the new version to be live
                    sh 'kubectl rollout status deployment/aceest-deployment'
                    
                    sh 'echo "--- Deployment Successful! ---"'
                }
            }
        }
    }
}