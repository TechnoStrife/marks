const fs = require('fs')
const chalk = require('chalk');

const FtpDeploy = require('ftp-deploy')
const ftp = new FtpDeploy()


const credentials = JSON.parse(fs.readFileSync('deployment-host.json', 'ascii'))

const config = {
    ...credentials,
    localRoot: __dirname,
    include: [
        '**/*.py',
        'static/**/*',
        'templates/*',
        'requirements.txt'
    ],
    exclude: [
        'manage.py',
        'static/**/*.map',
        'venv/**',
        'node_modules/**',
        'static/admin/**',
        'static/rest_framework/**'
    ],
    // deleteRemote: false,
    // forcePasv: true, // Passive mode is forced (EPSV command is not sent)
}

process.stdout.write('\rConnecting')

// ftp.on('uploading', data => {})
ftp.on('uploaded', function(data) {
    let progress = `${data.transferredFileCount}/${data.totalFilesCount}`
    process.stdout.write('\r' + ' '.repeat(80) + '\r')
    process.stdout.write(`Uploaded ${progress}  ${data.filename}`)
})
ftp.on('log', () => {
    process.stdout.write('.')
})

function print_files(folder, level=0) {
    let {files, ...subfolders} = folder
    for (const file of files)
        console.log('    '.repeat(level) + chalk.green(file))
    for (const [name, subfolder] of Object.entries(subfolders)) {
        console.log('    '.repeat(level) + name + '/')
        print_files(subfolder, level + 1)
    }
}

ftp.deploy(config)
    .then(res => {
        console.log()
        res = res.flat().map(filepath => {
            filepath = filepath.slice('uploaded '.length)
            filepath = filepath.slice(__dirname.length)
            if (filepath[0] === '/')
                filepath = filepath.slice(1)
            return filepath
        })
        let root = {files: []}
        for (const filepath of res) {
            let folders = filepath.split('/')
            let file = folders.splice(-1, 1)[0]
            let current_folder = root
            for (const folder of folders) {
                if (folder in current_folder)
                    current_folder = current_folder[folder]
                else
                    current_folder = current_folder[folder] = {files: []}
            }
            current_folder.files.push(file)
        }
        console.log('root/')
        print_files(root, 1)
    })
    .catch(err => console.log(err))
