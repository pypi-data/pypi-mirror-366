#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');
const os = require('os');

/**
 * BaaS SMS/MMS MCP Server - Node.js Wrapper
 * 
 * This wrapper script executes the Python MCP server and handles
 * cross-platform compatibility and dependency management.
 */

function findPython() {
    // Try common Python executable names
    const pythonCandidates = ['python3', 'python', 'py'];
    
    for (const pythonCmd of pythonCandidates) {
        try {
            const result = require('child_process').spawnSync(pythonCmd, ['--version'], { 
                stdio: 'pipe',
                encoding: 'utf8'
            });
            
            if (result.status === 0 && result.stdout.includes('Python 3.')) {
                return pythonCmd;
            }
        } catch (error) {
            // Continue trying next candidate
        }
    }
    
    throw new Error('Python 3.10+ 이상이 필요하지만 찾을 수 없습니다. Python 3.10 이상을 설치해주세요.');
}

function installDependencies(pythonCmd) {
    console.log('Python 의존성을 설치하는 중...');
    
    const requirementsPath = path.join(__dirname, 'requirements.txt');
    const installProcess = require('child_process').spawnSync(
        pythonCmd, 
        ['-m', 'pip', 'install', '-r', requirementsPath, '--quiet'], 
        { 
            stdio: 'inherit',
            cwd: __dirname
        }
    );
    
    if (installProcess.status !== 0) {
        console.error('Python 의존성 설치에 실패했습니다.');
        console.error('다음 명령어를 실행해주세요: pip install -r requirements.txt');
        process.exit(1);
    }
}

function checkDependencies(pythonCmd) {
    // Check if required packages are installed
    const checkProcess = require('child_process').spawnSync(
        pythonCmd,
        ['-c', 'import mcp, httpx; print("Dependencies OK")'],
        { stdio: 'pipe', encoding: 'utf8' }
    );
    
    if (checkProcess.status !== 0) {
        installDependencies(pythonCmd);
    }
}

function startMCPServer() {
    try {
        // Find Python executable
        const pythonCmd = findPython();
        console.log(`사용할 Python: ${pythonCmd}`);
        
        // Check and install dependencies if needed
        checkDependencies(pythonCmd);
        
        // Path to the Python MCP server
        const serverPath = path.join(__dirname, 'baas_sms_mcp', 'server.py');
        
        // Validate environment variables
        const requiredEnvVars = ['BAAS_API_KEY', 'PROJECT_ID'];
        const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);
        
        if (missingVars.length > 0) {
            console.warn(`경고: 누락된 환경변수: ${missingVars.join(', ')}`);
            console.warn('이 변수들이 없으면 서버가 정상적으로 작동하지 않을 수 있습니다.');
            console.warn('환경변수를 설정하거나 Claude Desktop 설정에서 추가해주세요.');
            console.warn('참고: BAAS_API_BASE_URL은 https://api.aiapp.link로 고정되었습니다');
        }
        
        // Start the Python MCP server
        console.log('BaaS SMS/MMS MCP 서버를 시작합니다...');
        const serverProcess = spawn(pythonCmd, [serverPath], {
            stdio: 'inherit',
            cwd: __dirname,
            env: process.env
        });
        
        // Handle process events
        serverProcess.on('error', (error) => {
            console.error('MCP 서버 시작에 실패했습니다:', error.message);
            process.exit(1);
        });
        
        serverProcess.on('exit', (code, signal) => {
            if (signal) {
                console.log(`MCP 서버가 시그널에 의해 종료되었습니다: ${signal}`);
            } else if (code !== 0) {
                console.error(`MCP 서버가 코드 ${code}로 종료되었습니다`);
                process.exit(code);
            }
        });
        
        // Handle termination signals
        process.on('SIGINT', () => {
            console.log('\nMCP 서버를 종료하는 중...');
            serverProcess.kill('SIGINT');
        });
        
        process.on('SIGTERM', () => {
            console.log('\nMCP 서버를 종료하는 중...');
            serverProcess.kill('SIGTERM');
        });
        
    } catch (error) {
        console.error('MCP 서버 시작 중 오류 발생:', error.message);
        console.error('\n문제 해결 방법:');
        console.error('1. Python 3.10+ 이상이 설치되어 있는지 확인');
        console.error('2. pip이 사용 가능한지 확인');
        console.error('3. 필수 환경변수 설정: BAAS_API_KEY, PROJECT_ID');
        process.exit(1);
    }
}

// Main execution
if (require.main === module) {
    startMCPServer();
}

module.exports = { startMCPServer };