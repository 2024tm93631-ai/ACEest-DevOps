// ──────────────────────────────────────────────────────────────────────────────
// ACEest Fitness & Gym - Jenkinsfile (Simplified Pipeline)
// Works with basic Jenkins installation - no extra plugins needed
// ──────────────────────────────────────────────────────────────────────────────

pipeline {
    agent any

    environment {
        APP_NAME     = 'aceest-fitness'
        IMAGE_LATEST = "${APP_NAME}:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                echo '=== Stage 1: Pulling latest code from GitHub ==='
                checkout scm
                echo "Build Number: ${env.BUILD_NUMBER}"
                echo "Job Name: ${env.JOB_NAME}"
            }
        }

        stage('Verify Files') {
            steps {
                echo '=== Stage 2: Verifying project files ==='
                sh 'ls -la'
                sh 'cat requirements.txt'
                echo "All required files present!"
            }
        }

        stage('Lint') {
            steps {
                echo '=== Stage 3: Running Lint Check ==='
                sh '''
                    pip install flake8 --quiet --break-system-packages 2>/dev/null || pip install flake8 --quiet
                    python -m flake8 app.py test_app.py --select=E9,F63,F7,F82 --show-source || python3 -m flake8 app.py test_app.py --select=E9,F63,F7,F82 --show-source
                    echo "Lint check passed!"
                '''
            }
        }

        stage('Unit Tests') {
            steps {
                echo '=== Stage 4: Running Unit Tests ==='
                sh '''
                    pip install flask pytest pytest-cov --quiet --break-system-packages 2>/dev/null || pip install flask pytest pytest-cov --quiet
                    python -m pytest test_app.py -v --tb=short || python3 -m pytest test_app.py -v --tb=short
                    echo "All unit tests passed!"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '=== Stage 5: Building Docker Image ==='
                sh "docker build -t ${IMAGE_LATEST} ."
                sh "docker images ${APP_NAME}"
                echo "Docker image built successfully!"
            }
        }

        stage('Docker Verify') {
            steps {
                echo '=== Stage 6: Verifying Docker Image ==='
                sh "docker inspect ${IMAGE_LATEST}"
                sh "docker run --rm ${IMAGE_LATEST} python3 -c \"import app; print('App imports successfully!')\""
                echo "Docker image verified successfully!"
            }
        }

    }

    post {
        success {
            echo '''
            =============================================
             BUILD SUCCESS - ACEest CI/CD Pipeline
            =============================================
             All stages completed:
              - Checkout           SUCCESS
              - Verify Files       SUCCESS
              - Lint               SUCCESS
              - Unit Tests         SUCCESS
              - Docker Build       SUCCESS
              - Docker Test        SUCCESS
            =============================================
            '''
        }
        failure {
            echo '''
            =============================================
             BUILD FAILED - ACEest CI/CD Pipeline
            =============================================
             Check the logs above for the failing stage.
            =============================================
            '''
        }
        always {
            sh "docker rmi ${IMAGE_LATEST} || true"
            cleanWs()
        }
    }
}
