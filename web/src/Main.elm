module Main exposing (..)
import Html
import Html.Attributes
import Html.Events
import Browser
import Json.Encode as E
import Json.Decode as D
import Html.Events
import Http
import Url.Builder

type alias Location = String

type alias Model = { location: Location , routes: List Route, err : String }

type alias Route = {start: Location, end: Location}

type Msg = 
    UpdateLocation Location 
    | SubmitForm 
    | GotRoutes (Result Http.Error (List Route))

main : Program E.Value Model Msg
main =
    Browser.document
        { init = init
        , update = update
        , subscriptions = \_ -> Sub.none
        , view = view
        }

init : E.Value -> (Model, Cmd Msg)
init _ = ( { location = "", routes = [] , err = "" }, Cmd.none)

update : Msg -> Model -> (Model, Cmd Msg)
update msg model = 
    case msg of 
        UpdateLocation newLocation ->
            ({model | location = newLocation}, Cmd.none)

        SubmitForm -> 
            (model, getRoutes model.location)

        GotRoutes maybeRoutes ->
            case maybeRoutes of
                Ok routes ->
                    ({model | routes = routes, err = ""}, Cmd.none)

                Err error ->
                    case error of
                        Http.BadStatus status ->
                            ({model | err = "Server error. Code " ++ String.fromInt status }, Cmd.none)

                        _ -> 
                            ({model | err = "Server error." }, Cmd.none)

-- REGION HTTP

getRoutes : Location -> Cmd Msg
getRoutes location =
    Http.get { url= Url.Builder.absolute ["api", "routes" ] [Url.Builder.string "location" location ], expect = Http.expectJson GotRoutes routesDecoder }

routesDecoder : D.Decoder (List Route)
routesDecoder =
    D.list routeDecoder
        
routeDecoder : D.Decoder Route
routeDecoder =
    D.map2 Route
        (D.field "start" D.string)
        (D.field "end" D.string)


-- ENDREGION


view : Model -> Browser.Document Msg
view model =
    Browser.Document "Tricky Treaters" [
        Html.div [] [
            Html.input [Html.Events.onInput UpdateLocation, Html.Attributes.value model.location][],
            Html.button [Html.Events.onClick SubmitForm] [Html.text "Submit" ]
            , Html.p [] [Html.text model.err ]
            ]
    ]
