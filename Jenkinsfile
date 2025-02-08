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
                        url: 'https://github.com/FX411/jenkins-tests.git'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
                }
            }
        }

        stage('Remove Old Container') {
            steps {
                script {
                    sh "docker stop ${CONTAINER_NAME} || true"
                    sh "docker rm ${CONTAINER_NAME} || true"
                }
            }
        }

        stage('Run New Container') {
            steps {
                script {
                    sh "docker run -d -p 3000:3000 --name ${CONTAINER_NAME} ${IMAGE_NAME}:${IMAGE_TAG}"
                }
            }
        }
    }
}
