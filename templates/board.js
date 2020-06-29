// Refresh each element every X millesconds
'use strict';
var INTERVAL = 2000;

$(document).ready(function() {
    var handHash = undefined;  // hash of most recently rendered hand, or undefined
    var cardsHash = undefined;  // hash of most recently rendered current cards, or undefined
    var votesHash = undefined;  // hash of most recently revealed votes, or undefined
    var usersHash = undefined;  //hash of players and their colors
    var gameHash = undefined;
    var gameStarted = false;
    var selectedCard = undefined;
    
    $('.collapse').click(toggleHand);

    $('#startGameContainer').hide();
    
    var gameBoardWorker = function worker(){
        $.getJSON('gamePlay?cmd='+ {{ commands.GET_BOARD }}, function(data){
            if(data.host == data.user){
                $('#startGameContainer').show();
            }
            if(data.state == {{states.BEGIN}}){ //Waiting for someone to start game
                console.log('Waiting game start');
            }else{
                gameStarted = true;
                $('#startGameContainer').hide();
                $('#bunnyPalette').hide();
            }
            
            //else the game has started 
            var numPlayers = data.order.length;
            var clueMaker = data.order[data.turn];
            var usersHtml = [];
            //refresh all bunnies
            $('.bunnyTaken').addClass('clickable').removeClass('bunnyTaken');
            
            var maxRank = 0;
            $.each(data.ranked, function(puid, rank) {
                if (rank > maxRank) {
                    maxRank = rank;
                }
            });

            $.each(data.order, function(i, puid) {
                var isWinner = (data.state == {{ states.END }} && data.ranked[puid] == maxRank);
                
                var user = data.players[puid];
                
                var imgUse = undefined;
                
                if (data.state == {{ states.BEGIN }}){
                    imgUse = '<img class="thinking" height=20px src="{{ display.Images.ICON_ACTIVE }}" title="Thinking" />';
                }else if(i == data.turn){
                    imgUse = '<img class="thinking" height=20px src="{{ display.Images.YOUR_TURN }}" title="Thinking" />';
                }else if (data.requiresAction[puid]) {
                    imgUse = '<img class="thinking" height=20px src="{{ display.Images.THINKING }}" title="Thinking" />';
                } else if (data.state == {{ states.PLAY }}) {
                    imgUse = '<img height=20px src="{{ display.Images.CARD_BACK }}" title="Selected card" />';
                } else if (data.state == {{ states.VOTE }}) {
                    imgUse = '<img height=20px src="{{ display.Images.VOTE_TOKEN }}" title="Voted" />';
                }
                
                
                usersHtml.push('<tr height=30px' + (isWinner?'style="font_weight:bold">':'>'));//start table making
                if(imgUse != undefined){
                    usersHtml.push('<td width=20px>'+ imgUse + '</td>');//Action to be taken
                }else{
                    usersHtml.push('<td width=20px></td>');//Nothing to be done
                }
                
                usersHtml.push('<td width=30px> <img src= "{{ display.Images.BUNNY_READY }}" height=30px style="background:' + user.color_val + '; background-size: 95% 95%;"/></td>');//Bunny Color
                usersHtml.push('<td>' + user.name + '</td>');
                usersHtml.push('<td>' + user.score + '</td>');
                if(isWinner){
                    usersHtml.push('<td>' + smilifyText('(winner)', '{{ display.WebPaths.SMILIES }}') + '</td>');
                }
                usersHtml.push('</tr>');//end table making
                
                $('#' + user.color).removeClass('clickable').addClass('bunnyTaken');//Color is gone
            
            });
            
            $('#userTable').html(usersHtml.join(''));//Add table to userLists
            
            
            if (data.round.clue !== undefined) {
                $('#outsideClue').html('Clue: "' + data.round.clue + '"').fadeIn();
            } else {
                $('#outsideClue').hide();
            }
            
            // Render hand if changed
            if (data.player.handHash != handHash) {
                handHash = data.player.handHash;
                updateCards(data.player.hand, '#hands');
                   
            }
            
            // Render current cards if changed
            if (data.round.cardsHash != cardsHash) {
                cardsHash = data.round.cardsHash;
                updateCards(data.round.cards, '#cards');
                
            }
            
            
            if(gameHash == data.gamehash){
                console.log('awaiting game state to change')
                return;
            }else{
                gameHash = data.gamehash;
                $('#myModal').hide();
            }
            
            
            
            if(data.state == {{ states.CLUE }} && clueMaker == data.user){//I am cluemaster and am giving clue
                if($('.collapse').html() == '^'){
                    toggleHand();
                }
            
                console.log('Give clue')
                $('#caption').html('Give a Clue');
                
                $('#outsideClue').html('YOUR TURN').fadeIn();
                
                
                $('#hintImgCard').show();
                $('#submitImgCard').show();
                $('#submitImgCard').html('Submit Card and Clue')
                
                $('.boxImgH').click(imgClickFunc);
                $('.boxImgC').unbind();
                
                $('#submitImgCard').click(function(e){
                    $.getJSON('gamePlay?cmd='+ {{ commands.CREATE_CLUE }} + '&cid=' +selectedCard + '&clue=' + $('#hintImgCard').val(), function(e){
                       refreshGameBoard() ;
                    });
                });
                
            }else if(data.state == {{ states.PLAY }} && data.requiresAction[data.user]){//I need to submit a card
                console.log('Give card for clue')
            
                $('#caption').html(data.round.clue);
                
                $('#hintImgCard').hide();
                $('#submitImgCard').html('Submit Card');
                $('#submitImgCard').show();
                
                $('.boxImgH').click(imgClickFunc);
                $('.boxImgC').unbind();
                
                $('#submitImgCard').click(function(e){
                    $.getJSON('gamePlay?cmd='+ {{ commands.PLAY_CARD }} + '&cid=' +selectedCard, function(e){
                       refreshGameBoard() ;
                    });
                });
                
            }else if (data.state == {{ states.VOTE }} && data.requiresAction[data.user]){//I need to submit a vote
                $('#caption').html(data.round.clue)
                
                $('#hintImgCard').hide();
                $('#submitImgCard').html('Vote');
                $('#submitImgCard').show();
                
                $('.boxImgH').unbind();
                $('.boxImgC').click(imgClickFunc);
                
                
                $('#submitImgCard').click(function(e){
                    $.getJSON('gamePlay?cmd='+ {{ commands.CAST_VOTE }} + '&cid=' +selectedCard, function(e){
                       refreshGameBoard() ;
                    });
                });
                
            }else{
                $('#caption').html('');
                
                $('#hintImgCard').hide();
                $('#submitImgCard').hide();
                $('#submitImgCard').unbind();
                
                $('.boxImgH').click(imgClickFunc);
                $('.boxImgC').click(imgClickFunc);
            }
            
            //If votes changed who voted for what
            
            if (data.round.votesHash != votesHash) {
                votesHash = data.round.votesHash;
                if (data.round.cards !== undefined) {
                    $.each(data.round.votes, function(puid, cid) {
                        var card = $('#' + cid);
                        var randomLeft = Math.ceil(card.position().left + (Math.random()*150));
                        var randomTop = Math.ceil(card.offset().top + (Math.random()*250));
                        card.append('<div class="token" title="' + data.players[puid]
                                  + '" style="left:' + randomLeft + 'px;top:' + randomTop
                                  + 'px;background:' + data.players[puid].color_val + '; background-size: 100% 100%;">&nbsp;</div>');
                    });
                    $('.token').fadeIn();
                    $.each(data.round.owners, function(puid, cid) {
                        if(puid == data.round.clueMaker){
                            return true;
                        }
                        var card = $('#' + cid);
                        card.append('<div class="classifyy" title="' + data.players[puid]
                                  + '" style="left:' + card.position().left + 'px;top:' + card.offset().top
                                  + 'px;background:' + data.players[puid].color_val + '; background-size: 100% 100%;">&nbsp;</div>');
                                  
                        card.css({'background' : data.players[puid].color_val,
                                  'background-size' : '100% 100%'});
                        card.attr('title', data.players[puid]);
                    });
                    $('.classifyy').fadeIn();
                    
                }
            }
            
            
            
            
            
        }).always(function() {
            setTimeout(gameBoardWorker, INTERVAL);
        });
    };
    
    gameBoardWorker();
    
    function refreshGameBoard() {
        setTimeout(gameBoardWorker, 100);
    };
    
    function cardCell(card, chr) {
       // return '<div class="card" id="' + card.cid + '" hack="' + hack + '">'
        //      + '<img class="small" src="' + card.url + '" />'
         //     + '</div>';
        return '<div class="boxImg'+ chr+'" id="'+ card.cid +'"><img width=100% src="' + card.url +'"></div>'
        
    }
    
    function updateCards(cards, containerId) {
        if (cards === undefined) {
            $(containerId).html('');
            return
        }
        var html = [];
        var chr = 'C';
        
        if(containerId == '#hands'){        
            chr = 'H';
        }

        html.push('<div class="imageRow'+chr+'">');
        $.each(cards, function(i, card) {
            html.push(cardCell(card, chr));
            
        });
        html.push('</div>')
        $(containerId).html(html.join('')).fadeIn();
    }
    
    // Handler to choose bunny color
    $('.bunnyPicker').click(function(e) {
        $.getJSON('gamePlay?cmd=' + {{ commands.changeColor }} + '&' + 'color=' + $(this).attr('id'), function(data) {
                    refreshGameBoard();
        });
        
        e.preventDefault();
    });
    

    
    
    function toggleHand(){
       if($('.collapse').html() == '^'){
        //if($('.imageRow').css('maxHeight')){
           $('.imageRowH').show();
           $('.collapse').html('v');
           
           //$('.imageRow').css('maxHeight', $('.imageRow').scrollHeight + "px");
       } else{
           $('.imageRowH').hide();
           $('.collapse').html('^');
           //$('.imageRow').css('maxHeight', 'null');
       }
    }
    
    
    //To start the game
    $('#startGame').submit(function(e) {
        $.getJSON('gamePlay?cmd=' + {{ commands.START_GAME }}, function(data) {
            refreshGameBoard();
        });
        e.preventDefault();
    });
    
    
    //MODAL CONTENT
    var imgClickFunc = function(e){
      
      $('#myModal').show();
      $('#img01').attr('src', $('#' + e.currentTarget.id).children().attr('src'));
      //$('#img01').style('width:150%;')
      selectedCard = e.currentTarget.id;
      
      
    }

    // When the user clicks on <span> (x), close the modal
    $('.closeModal').click(function(e) {
      $('#myModal').hide();
    }); 
    $(document).keyup(function(e) {
        if (e.keyCode == 27) { // Esc keycode
            $('#myModal').hide();
        }
    }); 

});