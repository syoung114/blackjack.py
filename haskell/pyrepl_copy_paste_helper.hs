import Data.List (intersperse)
import Data.List.Split (splitOn)

-- ghci> let c = "deque([Card(rank=<Rank.TWO: (0, 2)>, suit=<Suit.CLUB: 1>), Card(rank=<Rank.THREE: (0, 3)>, suit=<Suit.SPADE:1>)])"
-- ghci> makeDefineableDeck c
-- "Card(Rank.TWO,Suit.CLUB),Card(Rank.THREE,Suit.SPADE)"
--
-- In other words, it removes the REPL gunk that prevents me from pasting the output to define a new variable.
--
makeDefineableDeck :: String -> String
makeDefineableDeck xs =
  concat
  $ intersperse ","
  $ map
    singleClean
    (
      splitOn "), " $ concat $ tail $ splitOn "[" $ head $ splitOn "]" xs
    )
  where
    singleClean :: String -> String
    singleClean xs =
      "Card("
      ++
        (
          concat
            $ intersperse ","
            $ filter (\x -> length x /= 0)
            $ map 
              (
                \x -> head $ splitOn ":" $ concat $ tail $ splitOn "=<" x
              )
            $ splitOn ", "
            $ concat
            $ tail
            $ splitOn "(" xs
        )
       ++ ")"

makeDefineableDeckPretty :: String -> String
makeDefineableDeckPretty xs = "deque([" ++ (makeDefineableDeck xs) ++ "])"
