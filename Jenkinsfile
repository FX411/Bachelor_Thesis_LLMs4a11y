pipeline {
    agent any

    environment {
        IMAGE_NAME = "test-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "test-website"
        TEST_IMAGE_NAME = "accessibility-tests"
        NETWORK_NAME = "test-network"
    }

    stages {
        stage('Git Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'ssh',
                        url: 'git@github.com:FX411/jenkins-tests.git'
                }
            }
        }

        stage('Setup Environment') {
            steps {
                script {
                    sh '''
                        echo "Setze Rechte für Python-Skript..."
                        chmod +x pythonhexerei.py
                        
                        echo "Führe Python-Skript aus..."
                        /opt/miniconda3/bin/python3 pythonhexerei.py
                    '''
                }
            }
        }

        stage('Build and Run Website Container') {
            steps {
                script {
                    sh '''
                        echo "Baue Docker-Image für die Website..."
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

                        echo "Erstelle Docker-Netzwerk (falls nicht vorhanden)..."
                        docker network create ${NETWORK_NAME} || true

                        echo "Stoppe und entferne alten Website-Container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true

                        echo "Starte neuen Website-Container..."
                        docker run -d --network=${NETWORK_NAME} -p 3000:3000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Warte auf Server-Start..."
                        sleep 10
                    '''
                }
            }
        }

        stage('Build and Run Test Container') {
            steps {
                script {
                    sh '''
                        echo "Baue Docker-Image für Accessibility-Tests..."
                        docker build -t ${TEST_IMAGE_NAME} -f Dockerfile.test .

                        echo "Starte Accessibility-Tests..."
                        docker run --network=${NETWORK_NAME} ${TEST_IMAGE_NAME}
                    '''
                }
            }
        }
    }

    post {
        always {
            script {
                sh '''
                    echo "Stoppe Website-Container..."
                    docker stop ${CONTAINER_NAME} || true

                    echo "Entferne Website-Container..."
                    docker rm ${CONTAINER_NAME} || true

                    echo "Entferne Docker-Netzwerk..."
                    docker network rm ${NETWORK_NAME} || true
                '''
            }
        }
    }
}
