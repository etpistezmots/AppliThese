function EnArrEnAvt(AdresseArr, AdresseAvt) {


    // IMPLEMATION CTRL + S pour Suite et CTRL + R pour Retour
    // d'après https://www.yosko.net/article33/snippet-06-javascript-capturer-des-raccourcis-clavier-utilises-par-votre-navigateur
    //must be accessible from both keydown and keypress events

    var cancelKeypress = false;

    document.addEventListener('keydown', function (e){
        if(e.ctrlKey && e.keyCode == 'S'.charCodeAt(0)) {
            //do this prior to anything else
            cancelKeypress = true;

            //might still be useful for other browsers
            e.preventDefault();

            window.location.replace(AdresseAvt);
        };
        if(e.ctrlKey && e.keyCode == 'R'.charCodeAt(0)) {
            //do this prior to anything else
            cancelKeypress = true;

            //might still be useful for other browsers
            e.preventDefault();

            window.location.replace(AdresseArr);
        }

    });

    //workaround for Firefox:
    document.addEventListener('keypress', function (e){
        //must probably be done prior to anything else
        if(cancelKeypress === true) {
            e.preventDefault();
            cancelKeypress = false;
        }
    });
 }