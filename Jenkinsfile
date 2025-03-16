pipeline {
    agent any

    environment {
        IMAGE_NAME = "main-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "main-website"
        NETWORK_NAME = "main-network"
        REPORTS_DIR = "reports"
        FIRST_REPORT="pa11y_report_${env.BUILD_NUMBER}.json"
    }

    stages {
        stage('Git Checkout') {
            steps {
                script {
                    git branch: 'main',
                        credentialsId: 'ssh',
                        url: 'git@github.com:FX411/Bachelor_Thesis_LLMs4a11y.git'
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
                        docker run -d --network=${NETWORK_NAME} -p 3333:3333 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Warte auf Server-Start..."
                        sleep 10
                    '''
                }
            }
        }

        stage('Run First WCAG Test with pa11y-ci') {
            steps {
                script {
                    sh '''
                        echo "Baue den pa11y-ci Container..."
                        docker build -t pa11y-ci-tester-main -f Dockerfile.pa11y .

                        echo "Erstelle Reports-Ordner..."
                        mkdir -p ${REPORTS_DIR}

                        echo "Starte Accessibility-Tests..."
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester-main || true

                        echo "Speichere den WCAG-Report..."
                        mv ${REPORTS_DIR}/pa11y-report.json ${REPORTS_DIR}/${FIRST_REPORT}
                    '''
                }
            }
        }

        stage('Archive First WCAG Report') {
            steps {
                script {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/${FIRST_REPORT}", fingerprint: true
                }
            }
        }
    }
}
