// functions
const connectToMetamask = () => {
    // function for get or update the address of user
    if (window.ethereum !== undefined) {
        // get address
        ganache = new Web3(window.ethereum)
        window.ethereum.request({method: 'eth_requestAccounts'})
            .then(accounts => {
                userAccount = ganache.utils.toChecksumAddress(accounts[0])
            })
            .catch(error => {
                console.log(error)
            })
        // update address
        window.ethereum.on('accountsChanged', accounts => {
            userAccount = ganache.utils.toChecksumAddress(accounts[0])
        })
    } else {
        console.log('not connected')
    }
}

// function for create a link. With this link the user can see his bids story
const showUpUserAccount = () => {
    let aElement = document.getElementById('account')
    if (userAccount !== undefined) {
        if(aElement === null) {
            let navElement = document.getElementsByTagName('nav')[0]
            let linkElement = document.createElement('a')
            linkElement.setAttribute('href', `/history/${userAccount}`)
            linkElement.setAttribute('id', 'account')
            linkElement.innerText = `${userAccount.substring(0, 6)}...${userAccount.substring(userAccount.length - 6)}`
            navElement.appendChild(linkElement)
        // update the text of button
        } else {
            aElement.innerText = `${userAccount.substring(0, 6)}...${userAccount.substring(userAccount.length - 6)}`
            aElement.setAttribute('href', `/history/${userAccount}`)
        }
    }
}

// function for send Ether to seller
const sendEther = async (wei, auction) => {
    // send ether to seller
    let hash = await ganache.eth.sendTransaction({
        from: userAccount,
        to: '0xb16761f7AAe8bF9f16C96792bB79579d0FD62752',
        value: wei
    })
    .then(receipt => {
        return receipt.transactionHash
    });
    // send hash to django
    fetch(`/hash/${hash}/${auction}`, {method: 'POST'})
        .then()
        .catch()
}


let userAccount
let ganache

setInterval(connectToMetamask, 1000)
setInterval(showUpUserAccount, 1000)