module.exports = {
    default: {
        paths: ['bddtests/features/*.feature'],
        require: ['bddtests/step_definitions/*.py'],
        requireModule: ['pytest-bdd'],
        format: ['progress']
    }
}