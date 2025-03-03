pipeline {
    agent any

    environment {
        IMAGE_NAME = "test-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "test-website"
        NETWORK_NAME = "test-network"
        REPORTS_DIR = "reports"
        FIRST_REPORT="before_transformation.json"
        SECOND_REPORT="after_transformation.json"
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

        stage('Run First WCAG Test with pa11y-ci') {
            steps {
                script {
                    sh '''
                        echo "Baue den pa11y-ci Container..."
                        docker build -t pa11y-ci-tester -f Dockerfile.pa11y .

                        echo "Erstelle Reports-Ordner..."
                        mkdir -p ${REPORTS_DIR}

                        echo "Starte Accessibility-Tests (Erster Durchlauf)..."
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester

                        echo "Speichere den ersten WCAG-Report..."
                        mv ${REPORTS_DIR}/pa11y-report.json ${REPORTS_DIR}/${FIRST_REPORT}
                    '''
                }
            }
        }

        stage('Remove website container') {
            steps {
                script {
                    sh '''
                        echo "Stoppe und entferne Website-Container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true
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

        stage('Python transformation') {
            steps {
                script {
                    sh '''
                        echo "Setze Rechte für Python-Skript..."
                        chmod +x pythonhexerei.py
                        
                        echo "Führe Python-Skript aus mit dem ersten WCAG-Report..."
                        /opt/miniconda3/bin/python3 pythonhexerei.py ${REPORTS_DIR}/${FIRST_REPORT}
                    '''
                }
            }
        }

        stage('Build and Run Transformed Website Container') {
            steps {
                script {
                    sh '''
                        echo "Baue Docker-Image mit transformiertem Code..."
                        docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

                        echo "Stoppe und entferne alten transformierten Website-Container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true

                        echo "Starte neuen transformierten Website-Container..."
                        docker run -d --network=${NETWORK_NAME} -p 3000:3000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}

                        echo "Warte auf Server-Start..."
                        sleep 10
                    '''
                }
            }
        }

        stage('Run Second WCAG Test with pa11y-ci (Transformed Website)') {
            steps {
                script {
                    sh '''
                        echo "Starte Accessibility-Tests (Zweiter Durchlauf, transformierte Website)..."
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester

                        echo "Speichere den zweiten WCAG-Report..."
                        mv ${REPORTS_DIR}/pa11y-report.json ${REPORTS_DIR}/${SECOND_REPORT}
                    '''
                }
            }
        }

        stage('Archive Second WCAG Report') {
            steps {
                script {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/${SECOND_REPORT}", fingerprint: true
                }
            }
        }
    }
}