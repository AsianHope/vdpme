#!groovy
def notifySlack(String buildStatus = 'STARTED') {
        // Build status of null means success.
        buildStatus = buildStatus ?: 'SUCCESS'
        def color

        if (buildStatus == 'STARTED') {
              color = '#D4DADF'
        } else if (buildStatus == 'SUCCESS') {
              color = '#BDFFC3'
        } else if (buildStatus == 'UNSTABLE') {
              color = '#FFFE89'
        } else {
              color = '#FF9FA1'
        }

        def msg = "${buildStatus}: `${env.JOB_NAME}` #${env.BUILD_NUMBER}:\n${env.BUILD_URL}console"

        slackSend(color: color, message: msg)
}

pipeline{
	agent any
	options {
		buildDiscarder(logRotator(numToKeepStr: '10', artifactNumToKeepStr: '10'))
	}
	stages {
            stage("Preparation") {
		steps {
			notifySlack()
                	git branch: 'next', credentialsId: '35d41123-6975-4d00-9bd7-67177509f1f0', url: 'git@github.com:AsianHope/vdpme.git'
		}
            }
            stage("Build") { 
		steps {
			script{
				sh'''	PYENV_HOME=$WORKSPACE/.pyenv/
	                             	# Delete previously built virtualenv
	                            	if [ -d $PYENV_HOME ]; then rm -rf $PYENV_HOME
					fi
	                                # Create virtualenv and install necessary packages
	                            	virtualenv --no-site-packages $PYENV_HOME
	                            	. $PYENV_HOME/bin/activate
	                            	pip install --quiet -r requirements.txt
					ssh root@jethro.asianhope.org 'bash /opt/scripts/pickbackup.sh'
                                        gunzip -f -d /opt/jenkins/*.gz
                                        mv -fT /opt/jenkins/jethro-live*.sql /opt/jenkins/vdpme.sql
					mysql -udjango -pdjango vdpme < /opt/jenkins/vdpme.sql
					python manage.py makemigrations
					python manage.py migrate
					'''
			}
		}
            }
	}
        post {
	    unstable {
		script {
				currentBuild.result = "UNSTABLE"
				echo "build unstable"
				notifySlack(currentBuild.result)
		}
	    }
	    success {
		script {
				currentBuild.result = "SUCCESS"
				echo "build success"
				def status = sh(returnStatus: true, script:'''git checkout master
				     git merge next 
	                             git push origin master
	                             cd /opt/jenkins/jethro/
				     ansible-playbook /opt/jenkins/jethro/site.yml''')
				if (status != "0") {
					currentBuild.result = "FAILED"
				}
				notifySlack(currentBuild.result)
		}
	    }
            failure {
                script{
                                currentBuild.result = "FAILED"
                                echo "build failed" 
				notifySlack(currentBuild.result)
                }               
            }   
            always {
		script {
//				junit '**/target/*.xml'
//				archive 'target/*.jar'
//				notifySlack(currentBuild.result)
				echo "end of build"
//				sh "rm /opt/jenkins/vdpme.sql"
		}
	   }
        }
}
//
