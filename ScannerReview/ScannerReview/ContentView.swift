//
//  ContentView.swift
//  ScannerReview
//
//  Created by Dale Carman on 4/8/23.
//

import SwiftUI

struct ContentView: View {
    var body: some View {
        /*#-code-walkthrough(ContentView.tabView)*/
        TabView {
            /*#-code-walkthrough(ContentView.tabView)*/
            /*#-code-walkthrough(ContentView.homeTab)*/
            HomeView()
            /*#-code-walkthrough(ContentView.homeTab)*/
            /*#-code-walkthrough(ContentView.tabItem)*/
                .tabItem {
                    Label("Home", systemImage: "person")
                }
            /*#-code-walkthrough(ContentView.tabItem)*/

            StoryView()
                .tabItem {
                    Label("Story", systemImage: "book")
                }
            
            FavoritesView()
                .tabItem {
                    Label("Favorites", systemImage: "star")
                }
            
            FunFactsView()
                .tabItem {
                    Label("Fun Facts", systemImage: "hand.thumbsup")
                }
            /*#-code-walkthrough(ContentView.addATab)*/
            //#-learning-task(addATab)
            
            /*#-code-walkthrough(ContentView.addATab)*/
        }
        
        
    }
}

struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
