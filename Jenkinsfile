pipeline {
    agent any

    environment {
        IMAGE_NAME = "test-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "test-website"
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

        stage('Python transformation') {
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

                        echo "Stoppe und entferne alten Website-Container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true

                        echo "Starte neuen Website-Container..."
                        docker run -d -p 3000:3000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Warte auf Server-Start..."
                        sleep 10
                    '''
                }
            }
        }

        stage('Run WCAG Tests with pa11y-ci') {
            steps {
                script {
                    sh '''
                        echo "Baue den pa11y-ci Container..."
                        docker build -t pa11y-ci-tester -f Dockerfile.pa11y .

                        echo "Starte Accessibility-Tests..."
                        docker run --rm pa11y-ci-tester
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


                '''
            }
        }
    }
}
