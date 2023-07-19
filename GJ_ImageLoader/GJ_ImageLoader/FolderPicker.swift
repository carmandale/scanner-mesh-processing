//
//  FolderPicker.swift
//  GJ_ImageLoader
//
//  Created by Dale Carman on 4/7/23.
//

import Foundation

import SwiftUI

struct FolderPicker: NSViewRepresentable {
    @Binding var directoryURL: URL?
    
    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }
    
    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        DispatchQueue.main.async {
            self.presentPicker(from: view)
        }
        return view
    }
    
    func updateNSView(_ nsView: NSView, context: Context) {}
    
    private func presentPicker(from view: NSView) {
        let openPanel = NSOpenPanel()
        openPanel.prompt = "Select Folder"
        openPanel.allowedFileTypes = ["none"]
        openPanel.allowsOtherFileTypes = false
        openPanel.canChooseFiles = false
        openPanel.canChooseDirectories = true
        openPanel.canCreateDirectories = false
        
        openPanel.beginSheetModal(for: view.window!) { response in
            if response == .OK {
                self.directoryURL = openPanel.url
                NotificationCenter.default.post(name: .directoryURLChanged, object: nil)
            }
        }
    }
    
    class Coordinator: NSObject {
        var parent: FolderPicker
        
        init(_ parent: FolderPicker) {
            self.parent = parent
        }
    }
}

