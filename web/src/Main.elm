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

type alias Location = {address: String , city: String , state: String , zipCode: String}

type alias Model = { location: Location , routes: List Route, err : String , radius: String , walkDistance: String}

type alias Route = {start: Location, end: Location}

type Msg =
    UpdateAddress String
    | UpdateCity String
    | UpdateState String
    | UpdateZipCode String
    | SubmitForm
    | GotRoutes (Result Http.Error (List Route))
    | UpdateRadius String
    | UpdateWalkDistance String



main : Program E.Value Model Msg
main =
    Browser.document
        { init = init
        , update = update
        , subscriptions = \_ -> Sub.none
        , view = view
        }

init : E.Value -> (Model, Cmd Msg)
init _ = ( { location = { address = "" , city = "" , state = "" , zipCode = "" }, routes = [] , err = "" , radius = "" , walkDistance = ""}, Cmd.none)

update : Msg -> Model -> (Model, Cmd Msg)
update msg model =
    case msg of
        UpdateWalkDistance newWalkDistance ->
            ({model | walkDistance = newWalkDistance}, Cmd.none)

        UpdateRadius newRadius ->
            ({model | radius = newRadius}, Cmd.none)

        UpdateAddress newAddress ->
            let
                oldLocation = model.location
                newLocation =
                    { oldLocation | address = newAddress }
            in
            ({model | location = newLocation}, Cmd.none)

        UpdateCity newCity ->
            let
                oldLocation = model.location
                newLocation =
                    { oldLocation | city = newCity }
            in
            ({model | location = newLocation}, Cmd.none)

        UpdateState newState ->
            let
                oldLocation = model.location
                newLocation =
                    { oldLocation | state = newState }
            in
            ({model | location = newLocation}, Cmd.none)

        UpdateZipCode newZipCode ->
                let
                    oldLocation = model.location
                    newLocation =
                        { oldLocation | zipCode = newZipCode }
                in
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
    Http.get { url= Url.Builder.absolute ["api", "routes" ] [Url.Builder.string "location" "TODO" ], expect = Http.expectJson GotRoutes routesDecoder }

routesDecoder : D.Decoder (List Route)
routesDecoder =
    D.list routeDecoder

routeDecoder : D.Decoder Route
routeDecoder =
    D.map2 Route
        (D.field "start" locationDecoder)
        (D.field "end" locationDecoder)

locationDecoder : D.Decoder Location
locationDecoder =
    D.map4 Location
        (D.field "address" D.string)
        (D.field "city" D.string)
        (D.field "state" D.string)
        (D.field "zipcode" D.string)
-- ENDREGION


view : Model -> Browser.Document Msg
view model =
    Browser.Document "Tricky Treaters" [

        Html.div [Html.Attributes.class "container-fluid", Html.Attributes.class "hasBackground"] [

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "address-label" ][Html.text "Address: "]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "address-label" ][Html.text "City: "]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "address-label" ][Html.text "State: "]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "address-label" ][Html.text "Zip code: "]
                ]
            ],

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [ Html.Events.onInput UpdateAddress, Html.Attributes.value model.location.address, Html.Attributes.class "address-input" ][]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [ Html.Events.onInput UpdateCity, Html.Attributes.value model.location.city, Html.Attributes.class "address-input" ][]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [ Html.Events.onInput UpdateState, Html.Attributes.value model.location.state, Html.Attributes.class "address-input" ][]
                ],
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [ Html.Events.onInput UpdateZipCode, Html.Attributes.value model.location.zipCode, Html.Attributes.class "address-input" ][]
                ]
            ],

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "other-label" ][Html.text "Radius you want to stay in (miles): "]
                ],

                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.label [ Html.Attributes.class "other-label" ][Html.text "Distance you want to walk (miles): "]
                ]
            ],

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [Html.Events.onInput UpdateRadius, Html.Attributes.value model.radius, Html.Attributes.class "other-input"] []
                ],

                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.input [Html.Events.onInput UpdateWalkDistance, Html.Attributes.value model.walkDistance, Html.Attributes.class "other-input"] []
                ]
            ],

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.button [Html.Events.onClick SubmitForm] [Html.text "Submit" ]
                ]
            ],

            Html.div [Html.Attributes.class "row"] [
                Html.div [Html.Attributes.class "col", Html.Attributes.class "d-flex", Html.Attributes.class "justify-content-center"] [
                    Html.p [] [Html.text model.err ]
                ]
            ],

            Html.div [Html.Attributes.class "bottomLine"] [
            ]
        ]

    ]
