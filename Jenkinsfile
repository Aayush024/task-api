pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                echo 'Code checked out successfully'
            }
        }

        stage('Verify') {
            steps {
                sh '''
                    echo "Running inside Jenkins"
                    pwd
                    ls -la
                '''
            }
        }

    }

}