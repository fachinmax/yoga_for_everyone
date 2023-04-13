// functions
const connect = async () => {
    // fetch user account
    if(window.ethereum !== undefined) {
        ganache = await new Web3(window.ethereum)
        window.ethereum
            .request({method: 'eth_requestAccounts'})
            .then(accounts => {
                userAccount = ganache.utils.toChecksumAddress(accounts[0])
            })
            .then(modifyButton)
            .then(addElements)
            .catch((error) => {
                alert('Please connect to Metamask')
            });
        // detect if user change his account
        window.ethereum.on('accountsChanged', (accounts) => {
            userAccount = ganache.utils.toChecksumAddress(accounts[0])
        });
    } else {
        alert('Please connect to Metamask')
    }
}

// function to submit a user's bit to smart contract. After send the bid, submit a call to django for save on redis the transaction hash, amount of bid and bidder account
const bid = async () => {
    // user can submit on bid at the time
    let highestBid = await fetch('price')
        .then(receipt => {
            return receipt.json()
        })
        .then(value => {
            if(value.status === 'OK') {
                return value.response
            }
        })
        .catch(error => {
            alert(error)
        })
    // pick up the value of ether indicate by the user
    let bid = document.querySelector("input").value;
    if (bid !== '') {
        let bidWei = convertToWei(bid)
        if(highestBid < bidWei) {
            // submit bid transaction to django for save it on redis
            fetch(`register/${bidWei}/${userAccount}`, {method: "POST"})
                .then()
                .catch(error => {
                    alert(error)
                });
        } else {
            alert('You must send higher bid.')
        }
    } else {
        alert('Indicate amount of ether.')
    }
}

// change the text of button, remove and add a new listener for execute the bid function
const modifyButton = () => {
    let btn = document.getElementsByClassName('partecipate-button')[0]
    btn.remove()
    btn = document.createElement('button')
    btn.setAttribute('class', 'partecipate-button')
    btn.innerText = 'Bid'
    btn.addEventListener('click', bid)
    let section = document.getElementById('partecipate-section')
    section.appendChild(btn)
}

// function for adds input, label and select elements. These elements are going to use for send a bid by the user
const addElements = async () => {
    // create a label
    let labelElementInput = document.createElement('label')
    labelElementInput.setAttribute('for', 'bid')
    let textLabel = document.createTextNode('Indicate the amount of wei that do you want bid')
    labelElementInput.appendChild(textLabel)
    // create a input element with a specific minimum value
    let inputElement = document.createElement('input')
    inputElement.setAttribute('type', 'number')
    inputElement.setAttribute('id', 'bid')
    // create a section in which I insert the element above
    let inputSection = document.createElement('section')
    inputSection.appendChild(labelElementInput)
    inputSection.appendChild(inputElement)
    // variable which I'm going to use then when I create the option
    let weiConverted = await fetch('price')
        .then(response => {
            return response.json()
        })
        .then(value => {
            if(value.status === 'OK') {
                wei = convertFromWei(value.response)
                inputElement.setAttribute('min', wei.amount)
                return wei
            }
        })
        .catch(error => {
            inputElement.setAttribute('min', 0)
        });
    // create a label
    let labelElementSelect = document.createElement('label')
    labelElementInput.setAttribute('for', 'unit')
    textLabel = document.createTextNode('Select the unit of ether')
    labelElementSelect.appendChild(textLabel)
    // create select
    let selectElement = document.createElement('select')
    selectElement.setAttribute('id', 'unit')
    // create and add option in select
    let optionElement
    // variable which lets me know how many option create for each unit of ether
    let createOptions = false
    for (let unit in units) {
        if (units[unit] == weiConverted.unit || createOptions) {
            createOptions = true
            optionElement = document.createElement('option')
            optionElement.setAttribute('value', units[unit])
            optionElement.innerText = units[unit]
            selectElement.appendChild(optionElement)
        }
    }
    // create a section in which I insert the element above
    let selectSection = document.createElement('section')
    selectSection.appendChild(labelElementSelect)
    selectSection.appendChild(selectElement)
    // adds elements in DOM
    let sectionElement = document.getElementById('partecipate-section')
    let buttonElement = document.getElementsByTagName('button')[0]
    sectionElement.insertBefore(inputSection, buttonElement)
    sectionElement.insertBefore(selectSection, buttonElement)
}

// takes the amount in a unit of ether and converts it to the wei
const convertToWei = amount => {
    let typeUnit = document.getElementsByTagName('select')[0].value
    return ganache.utils.toWei(amount, typeUnit)
}

// takes the amount in wei and converts it to the nearest unit 
convertFromWei = amount => {
    let finalUnit = units[0]
    amount = '' + amount
    let finalAmount = amount
    let amountConverted
    for (let unit in units) {
        amountConverted = ganache.utils.fromWei(amount, units[unit])
        if (amountConverted < 1) {
            break
        } else {
            finalAmount = amountConverted
            finalUnit = units[unit]
        }
    }
    return {unit: finalUnit, amount: finalAmount}
}

// function for remove all child of a node
const removeAllChildNodes = parent => {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild)
    }
}

// countDown function
const countDown = async () => {
    let timeElement = document.getElementsByTagName('time')[0]
    let now = new Date().getTime()
    let gap = endTimeAuction - now
    if(gap > 0) {
        const seconds = 1000
        const minutes = seconds * 60
        const hours = minutes * 60
        const days = hours * 24
        const weeks = days * 7

        let textWeeks = Math.floor(gap / weeks)
        let textDays = Math.floor((gap % weeks) / days)
        let textHours = Math.floor((gap % days) / hours)
        let textMinutes = Math.floor((gap % hours) / minutes)
        let textSeconds = Math.floor((gap % minutes) / seconds)

        let textTime = textWeeks !== 0 ? `<span>${textWeeks} weeks</span>` : ''
        textTime += textDays !== 0 ? `<span>${textDays} days</span>` : ''
        textTime += textHours !== 0 ? `<span>${textHours} hours</span>` : ''
        textTime += textMinutes !== 0 ? `<span>${textMinutes} minutes</span>` : ''
        textTime += `<span>${textSeconds} seconds</span>`
        timeElement.innerHTML = textTime
    // when the auction end I delete the possibility for user to send new bids
    } else {
        timeElement.innerHTML = 'Auction ended. Thanks for take part.'
        let sectionElement = document.getElementById('partecipate-section')
        removeAllChildNodes(sectionElement)
    }
}

// function for update the price of auction product
const updatePrice = () => {
    if(ganache !== undefined) {
        fetch('price')
            .then(response => {
                return response.json()
            })
            .then(value => {
                if(value.status === 'OK') {
                    ether = convertFromWei(value.response)
                    document.getElementById('price').innerText = `${ether.amount} ${ether.unit}`
                }
            })
            .catch(error => {
                alert(error)
            })
    }
}

// function for update the bids list of every bidder
const updateBids = () => {
    // check if the user take a pert to the auction by control the text of the button used for send bids
    let button = document.getElementsByClassName('partecipate-button')[0]
    if (ganache !== undefined && button.innerText === 'Bid') {
        fetch('allBids')
            .then(response => {
                return response.json()
            })
            .then(data => {
                if (data.status === 'OK') {
                    let bids = data.response
                    let ulElement = document.getElementsByTagName('ul')[0]
                    removeAllChildNodes(ulElement)
                    for (let bid in bids) {
                        let liElement = document.createElement('li')
                        let bidDict = convertFromWei(bids[bid].wei)
                        liElement.innerText = `The ${bids[bid].address} bidded ${bidDict.amount} ${bidDict.unit}`
                        ulElement.appendChild(liElement)
                    }
                } else {
                    alert(data.response)
                }
            })
            .catch(error => {
                alert(error)
            })
    }
}


// global variables
let address;
const units = ['wei', 'kwei', 'mwei', 'gwei', 'microether', 'milliether', 'ether']

let time = + document.getElementsByTagName('time')[0].innerText
// I multiply by 1000 because the time get by django and the time get by javascript differ. This 1000 are the thousandths of seconds
const endTimeAuction = time * 1000
countDown()
setInterval(countDown, 1000)
setInterval(updatePrice, 1000)
setInterval(updateBids, 1000)