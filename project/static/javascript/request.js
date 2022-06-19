// Taken from https://stackoverflow.com/questions/321113/how-can-i-pre-set-arguments-in-javascript-function-call-partial-function-appli/321527#321527
// Based on https://developer.mozilla.org/en-US/docs/Web/Guide/AJAX/Getting_Started
// Probably want to replace with fetch according to https://code.tutsplus.com/articles/create-a-javascript-ajax-post-request-with-and-without-jquery--cms-39195

function partial(func /*, 0..n args */) {
  let args = Array.prototype.slice.call(arguments, 1);
  return function() {
    let allArguments = args.concat(Array.prototype.slice.call(arguments));
    return func.apply(this, allArguments);
  };
}

let httpRequest;

function setPostVariables(items) {
  let variables = {};
  for (let i = 0; i < items.length; i++) {
    variables[items[i].name] = items[i].value
  }
  for (let i = 0; i < variables.length; i++) {
    console.log(variables.value);
  }
  console.log(variables);
  return variables;
}

function setGetVariables(url, items) {
  let variables = [];
  for (let i = 0; i < items.length; i++) {
    variables.push(`${items[i].name}=${items[i].value}`)
  }
  variables = variables.join("&");
  return variables;
}

function makePostRequest(url, post, func) {
  httpRequest = new XMLHttpRequest();

  if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }

  httpRequest.open("POST", url, true);
  httpRequest.setRequestHeader('Content-Type', 'application/json; charset=UTF-8'); // Changed from application/x-www-form-urlencoded for POST instead of GET
  httpRequest.onreadystatechange = func;
  httpRequest.send(post);
}

function makeGetRequest(url, variables, func) {
  httpRequest = new XMLHttpRequest();

  if (!httpRequest) {
      console.log('Giving up :( Cannot create an XMLHTTP instance');
      return false;
    }

  httpRequest.open("GET", url + `?${variables}`, true);
  httpRequest.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded'); // Changed from application/x-www-form-urlencoded for POST instead of GET
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