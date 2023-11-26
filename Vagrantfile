Vagrant.configure("2") do |config|
  config.vm.provider :virtualbox do |vb|
    vb.customize ["modifyvm", :id, "--cpuexecutioncap", "80"]
  end

  #config.vm.provision :shell, path: "bootstrap.sh"

  config.vm.define :master do |master|
    master.vm.provider :virtualbox do |vb|
       vb.customize ["modifyvm", :id, "--memory", "4096"]
    end
    master.vm.box = "ubuntu/jammy64"
    master.vm.hostname = "master"
    master.vm.network "private_network", ip: "192.168.33.10"
    config.vm.provision :shell, inline: "echo Master"
    config.vm.provision :shell, path: "bootstrap.sh"
    config.vm.provision :shell, inline: "echo Master Ready and Bootstrapped"
  end

  %w{worker1}.each_with_index do |name, i|
    config.vm.define name do |worker|
      worker.vm.provider :virtualbox do |vb|
       vb.customize ["modifyvm", :id, "--memory", "4096"]
      end
      worker.vm.box = "ubuntu/jammy64"
      worker.vm.hostname = name
      worker.vm.network "private_network", ip: "192.168.33.#{i + 11}"
      config.vm.provision :shell, path: "bootstrap.sh"
      config.vm.provision :shell, inline: "echo worker #{i} Ready and Bootstrapped"
    end
  end
end