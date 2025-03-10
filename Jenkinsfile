pipeline {
    agent any

    environment {
        IMAGE_NAME = "openai-website"
        TRANSFORMED_IMAGE_NAME = "transformed-openai-website"
        IMAGE_TAG = "latest"
        CONTAINER_NAME = "openai-website"
        NETWORK_NAME = "test-network"
        REPORTS_DIR = "reports"
        FIRST_REPORT="before_transformation_${env.BUILD_NUMBER}.json"
        SECOND_REPORT="after_transformation_${env.BUILD_NUMBER}.json"
    }

    stages {
        stage('Git Checkout') {
            steps {
                script {
                    def branchName = env.BRANCH_NAME ?: 'main'  // Falls kein Branch gesetzt ist, Standard auf "main"
                    echo "Starte Checkout für Branch: ${branchName}"

                    git branch: branchName,
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
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester || true

                        echo "Speichere den ersten WCAG-Report..."
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

        stage('Python Dependencies') {
            steps {
                script {
                    sh '''
                        echo "Setze Rechte für Python-Skript..."
                        chmod +x gpt4o.py
                        
                        echo "Installiere Abhängigkeiten..."
                        /opt/miniconda3/bin/python3 -m pip install openai
                    '''
                }
            }
        }

        stage('Python LLM Transformation') {
            steps {
                script {
                    withCredentials([string(credentialsId: 'openaiapi', variable: 'OPENAI_API_KEY')]) {
                        sh '/opt/miniconda3/bin/python3 gpt4o.py ${REPORTS_DIR}/${FIRST_REPORT}' }
                }
            }
        }

        stage('Build and Run Transformed Website Container') {
            steps {
                script {
                    sh '''
                        echo "Baue Docker-Image mit transformiertem Code..."
                        docker build -t ${TRANSFORMED_IMAGE_NAME}:${IMAGE_TAG} .

                        echo "Stoppe und entferne alten Website-Container..."
                        docker stop ${CONTAINER_NAME} || true
                        docker rm ${CONTAINER_NAME} || true

                        echo "Starte neuen transformierten Website-Container..."
                        docker run -d --network=${NETWORK_NAME} -p 3000:3000 --name ${CONTAINER_NAME} ${TRANSFORMED_IMAGE_NAME}:${IMAGE_TAG}

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
                        docker run --rm --network=${NETWORK_NAME} -v $PWD/${REPORTS_DIR}:/app/reports pa11y-ci-tester || true

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
