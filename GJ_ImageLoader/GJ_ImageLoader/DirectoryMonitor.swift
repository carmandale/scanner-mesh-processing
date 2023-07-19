//
//  DirectoryMonitor.swift
//  GJ_ImageLoader
//
//  Created by Dale Carman on 4/7/23.
//

import Foundation

protocol DirectoryMonitorDelegate: AnyObject {
    func directoryDidUpdate(_ directoryMonitor: DirectoryMonitor)
}

class DirectoryMonitor {
    let url: URL
    private var source: DispatchSourceFileSystemObject?
    weak var delegate: DirectoryMonitorDelegate?
    
    init(url: URL) {
        self.url = url
    }
    
    deinit {
        stopMonitoring()
    }
    
    func startMonitoring() {
        let descriptor = open(url.path, O_EVTONLY)
        guard descriptor != -1 else { return }
        
        let queue = DispatchQueue(label: "com.example.directorymonitor")
        source = DispatchSource.makeFileSystemObjectSource(fileDescriptor: descriptor, eventMask: .write, queue: queue)
        
        source?.setEventHandler { [weak self] in
            self?.delegate?.directoryDidUpdate(self!)
        }
        
        source?.setCancelHandler {
            close(descriptor)
        }
        
        source?.resume()
    }
    
    func stopMonitoring() {
        source?.cancel()
    }
}
