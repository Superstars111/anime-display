// Taken from https://stackoverflow.com/questions/321113/how-can-i-pre-set-arguments-in-javascript-function-call-partial-function-appli/321527#321527

function partial(func /*, 0..n args */) {
  let args = Array.prototype.slice.call(arguments, 1);
  return function() {
    let allArguments = args.concat(Array.prototype.slice.call(arguments));
    return func.apply(this, allArguments);
  };
}

// Taken and modified from https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX/Getting_Started

let httpRequest;

function setVariables(url, items, result) {
  let variables = [];
  for (let i = 0; i < items.length; i++) {
    variables.push(`${items[i].name}=${items[i].value}`)
  }
  variables = variables.join("&")
  let func = partial(checkStatus, result);
  makeRequest(url, variables, func)
}

function makeRequest(url, variables, func) {
  httpRequest = new XMLHttpRequest();

  if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }

  httpRequest.open("GET", url + `?${variables}`);
  httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); //Don't understand what this header means
  console.log(func)
  httpRequest.onreadystatechange = func;
  httpRequest.send();
}

function checkStatus(func) {
  if (httpRequest.readyState === 4) {
    if (httpRequest.status === 200) {
      console.log("Data sent");
      //partial(setVariables, <url>, <element>, <func>) should be called on the appropriate event- <func> will be executed here.
      func()
    }
    else {
      console.log("Error: status = " + httpRequest.status);
    }
  }
}