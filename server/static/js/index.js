let board = null
let game = new Chess()

function generateMove(input_fen){
  // requesting flask server for best possible move
    $.ajax({
        url:'/handle_request',
        type: 'POST',
        dataType: 'json',
        data: input_fen,
        success: function(data) {
          let move = data.move
          // position validation runs on the server
          if (['Checkmate', 'Draw', 'Invalid fen'].includes(move)) {
            alert(move)
          } else {
            // applies move is the move is valid
            movePiece(move)
          }
        }
    })
}

$("#white").on('click', function() {
  // sets up board for white player view
  $('.btn-side').removeClass('btn-toggled')
  $(this).addClass('btn-toggled')
  let whiteConfig = {
    draggable: true,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    orientation: 'white'
  }
  board = Chessboard('board', whiteConfig)
  board.position(game.fen())
})

$("#black").on('click', function() {
  // sets up board for black player view
  $('.btn-side').removeClass('btn-toggled')
  $(this).addClass('btn-toggled')
  let blackConfig = {
    draggable: true,
    onDragStart: onDragStart,
    onDrop: onDrop,
    onSnapEnd: onSnapEnd,
    orientation: 'black'
  }
  board = Chessboard('board', blackConfig)
  board.position(game.fen())
  console.log(game.fen());
})

$('#start').on('click', function() {
  // activates bot and allows players to play
  if ($('#black').hasClass('btn-toggled')) {
    $('.info-text').css('visibility', 'visible')
    generateMove(game.fen())
  }
  // toggle on
  if ($(this).hasClass('btn-toggled')) {
    $(this).removeClass('btn-toggled')
    $(this).html('Start Game')
  // toggle off
  } else {
    $(this).addClass('btn-toggled')
    $(this).html('Stop Game')
  }
})

$('#reset').on('click', function() {
  // resets board to starting position
  board = Chessboard('board', config)
  game.load('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
  $('#start').removeClass('btn-toggled').text('Start Game')
})

$('#undo').on('click', function() {
  // resets a move
  game.undo()
  game.undo()
  board.position(game.fen())
})

function movePiece(move) {
  // engine plays move
  game.move(move)
  board.position(game.fen())
  $('.info-text').css('visibility', 'hidden')
}

function highlightSquare() {

}

function onDragStart (source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false
  if (!$('#start').hasClass('btn-toggled')) return false
  if ($('#white').hasClass('btn-toggled')) {
    side = 'w'
  } else {
    side = 'b'
  }

  // only pick up pieces for White
  if (side == 'w'){
  if (piece.search(/^b/) !== -1) return false
  }
  if (side == 'b') {
  if (piece.search(/^w/) !== -1) return false
  }
}

function onDrop (source, target) {
  // see if the move is legal
  let move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (move === null) return 'snapback'

  // make random legal move for black
  $('.info-text').css('visibility', 'visible')
  window.setTimeout(generateMove(game.fen()), 250)
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
  if (game.in_checkmate()) {
    alert('Checkmate')
  }
  if (game.in_draw() || game.in_stalemate() || game.in_threefold_repetition()) {
    alert('Draw')
  }

}

let config = {
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
}

board = Chessboard('board', config)
game.load(board.fen())