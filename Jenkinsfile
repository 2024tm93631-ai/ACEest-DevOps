// ──────────────────────────────────────────────────────────────────────────────
// ACEest Fitness & Gym - Jenkinsfile (Declarative Pipeline)
// Simplified pipeline using Docker agent for Python and Docker builds
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
                echo '=== Pulling latest code from GitHub ==='
                checkout scm
                echo "Commit: ${env.GIT_COMMIT}"
                echo "Branch: ${env.GIT_BRANCH}"
            }
        }

        stage('Verify Files') {
            steps {
                echo '=== Verifying project files ==='
                sh 'ls -la'
                sh 'cat requirements.txt'
            }
        }

        stage('Lint') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                echo '=== Running flake8 lint check ==='
                sh '''
                    pip install flake8 --quiet
                    flake8 app.py test_app.py --select=E9,F63,F7,F82 --show-source
                    echo "Lint passed!"
                '''
            }
        }

        stage('Unit Tests') {
            agent {
                docker {
                    image 'python:3.11-slim'
                    reuseNode true
                }
            }
            steps {
                echo '=== Running pytest unit tests ==='
                sh '''
                    pip install flask pytest pytest-cov --quiet
                    pytest test_app.py -v --tb=short
                    echo "All tests passed!"
                '''
            }
        }

        stage('Docker Build') {
            steps {
                echo '=== Building Docker image ==='
                sh "docker build -t ${IMAGE_LATEST} ."
                sh "docker images ${APP_NAME}"
                echo "Docker image built successfully!"
            }
        }

        stage('Docker Test') {
            steps {
                echo '=== Running tests inside Docker container ==='
                sh """
                    docker run --rm \
                        -v \$(pwd)/test_app.py:/app/test_app.py \
                        --entrypoint pytest \
                        ${IMAGE_LATEST} \
                        test_app.py -v --tb=short
                """
                echo "Docker tests passed!"
            }
        }

    }

    post {
        success {
            echo '''
            =============================================
             BUILD SUCCESS - ACEest CI/CD Pipeline
            =============================================
             All stages completed successfully:
              - Checkout
              - Verify Files
              - Lint
              - Unit Tests
              - Docker Build
              - Docker Test
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
