pipeline {
    agent any

    environment {
        IMAGE_NAME = "test-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "test-website"
        NETWORK_NAME = "test-network"
        REPORTS_DIR = "reports"
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
                        echo "Erstelle Docker-Netzwerk falls nicht vorhanden..."
                        docker network create ${NETWORK_NAME} || true

                        echo "Baue Docker-Image für die Website..."
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

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

        stage('Run WCAG Tests with pa11y-ci') {
            steps {
                script {
                    sh '''
                        echo "Baue den pa11y-ci Container..."
                        docker build -t pa11y-ci-tester -f Dockerfile.pa11y .

                        echo "Erstelle Reports-Ordner..."
                        mkdir -p ${REPORTS_DIR}

                        echo "Starte Accessibility-Tests..."
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester
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
                    docker rm ${CONTAINER_NAME} || true

                    echo "Entferne Docker-Netzwerk..."
                    docker network rm ${NETWORK_NAME} || true
                '''
            }
            archiveArtifacts artifacts: 'reports/pa11y-report.json', fingerprint: true
        }
    }
}
